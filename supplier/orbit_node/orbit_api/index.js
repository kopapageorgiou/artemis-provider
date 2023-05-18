import OrbitDB from 'orbit-db'
import { create } from 'ipfs-http-client'
import { program } from 'commander';
import express from 'express';
import fs from 'fs';
const app = express();
const PORT = 3000;

var ipfs; 
var orbitdb;

program
    .option('--orbitdb-dir <path>', 'path to orbitdb directory', './orbitdb')
    .option('--ipfs-host <host>', 'host to listen on', process.env.IPFS)
    .option('-p, --ipfs-port <port>', 'port to listen on', '5001');

program.parse();
const options = program.opts();


var _dataBases = {};
var _replicating = [];
app.use(express.json());

/**
 * * METHODS
 */

/**
 * Method to return database information
 * @param {let} name - The database name
 * @returns {dict} - The info for the particular database in dictionary format
 */
function infoDatabase(name){
    var db = _dataBases[name];
    if (!db) return {};
    return {
        address: db.address,
        dbname: db.dbname,
        id: db.id,
        options: {
            create: db.options.create,
            indexBy: db.options.indexBy,
            localOnly: db.options.localOnly,
            maxHistory: db.options.maxHistory,
            overwrite: db.options.overwrite,
            path: db.options.path,
            replicate: db.options.replicate,
        },
        type: db.type,
        uid: db.uid
    };
}

/**
 * Method to query data from a database
 * @param {let} db - The object representing the database
 * @param {let} attribute - The date that shipment is planned
 * @param {let} operator - The operator used to query the data
 * @param {let} value - The value to be compared in order to query the data
 * @returns {let} - The query results in dict format
 */
function getQuery(db, attribute, operator, value){
    switch(operator){
        case 'eq':
            return db.query((doc) => doc[attribute] === value);
        case 'ne':
            return db.query((doc) => doc[attribute] !== value);
        case 'gt':
            return db.query((doc) => doc[attribute] > value);
        case 'lt':
            return db.query((doc) => doc[attribute] < value);
        case 'gte':
            return db.query((doc) => doc[attribute] >= value);
        case 'lte':
            return db.query((doc) => doc[attribute] <= value);
        default:
            return db.query((doc) => doc[attribute] === value);
    }
}

/**
 * ! DEPRICATED. Probably will be removed
 */
function writeID(name, id){
    const path = '/home/mightypapas/Desktop/Projects/Artemis/provider/orbit_api/db_ids.json';
    try{
        if(fs.existsSync(path)){
            fs.readFile(path, 'utf8', function readFileCallback(err, data){
                if (err){
                    console.log(err);
                } else {
                    obj = JSON.parse(data);
                    obj[name] = id;
                    json = JSON.stringify(obj);
                    fs.writeFile(path, json, 'utf8', function(err){
                        if(err){
                            console.error(err);
                        }
                    });
                }
            });
        }
        else{
            const data = {name: id};
            fs.writeFile(path, JSON.stringify(data), 'utf8', function(err){
                if(err){
                    console.error(err);
                }
            });
        }
    } catch (error){
        console.error(error);
    }
}

/**
 * ! DEPRICATED. Probably will be removed
 */
function checkIfExists(name){
    const path = '/home/mightypapas/Desktop/Projects/Artemis/provider/orbit_api/db_ids.json';
    fs.readFile(path, 'utf8', function readFileCallback(err, data){
        if (err){
            console.log(err);
        } else {
            obj = JSON.parse(data);
            if(obj[name]){
                return obj[name];
            } else {
                return false;
            }
        }
    });
}

/**
 * * ENDPOINTS
 */

/**
 * Endpoint to insert measurements in shared databases
 * @method: POST
 * @body: JSON
 * @param {let} order_id - The order id
 * @param {let} shipment_date - The date that shipment is planned
 * @param {let} enc_customer_id - The customer id that order concerns (encrypted value)
 * @param {int} enc_stop_id - The stop id of the customer id (encrypted value)
 * @param {let} vehicle_id - The vehicle id that has taken over the shipment
 * @param {let} abe_enc_key - The encrypted symmetric key
 */
app.post('/insertOrders', async (req, res) => {
    try{
        const {order_id} = req.body;
        const {shipment_date} = req.body;
        const {enc_customer_id} = req.body;
        const {enc_stop_id} = req.body;
        const {vehicle_id} = req.body;
        const {abe_enc_key} = req.body;

        _dataBases['shared.orders'].put({order_id: order_id,
                                            shipment_date: shipment_date,
                                            enc_customer_id: enc_customer_id,
                                            enc_stop_id: enc_stop_id,
                                            vehicle_id: vehicle_id,
                                            abe_enc_key: abe_enc_key});

        res.status(200).send({
            'info': 'Data inserted successfully',
            'data_base': infoDatabase('shared.orders')
        });


    }
    catch (error){
        console.error('ERR | in /insertOrders:', error);
        res.status(500).send({
            'info': 'Could not store data to database'
        });
    }
});

/**
 * Endpoint to get all data from a database
 * @method: POST
 * @body: JSON
 * @param {let} name - The name of the database
 */
app.post('/getData', async (req, res) => {
    try{
        console.log(_dataBases);
        const {name} = req.body;
        var dataRes;
        dataRes = _dataBases[name].get('');
        res.status(200).send({
            'info': 'Data fetched successfully',
            'data': dataRes
        });
    } catch (error){
        console.error('ERR | in /getData:', error.message);
        res.status(500).send({
            'info': 'Could not get data from database'
        });
    }
    
});

/**
 * Endpoint to query data from databases
 * @method: POST
 * @body: JSON
 * @param {let} name - The name of the database
 * @param {let} attribute - The attribute that the query will be based on
 * @param {let} operator - The operator used to query the data
 * @param {let} value - The value to be compared in order to query the data
 */
app.post('/queryData', async (req, res) => {
    try{
        const {name} = req.body;
        const {operator} = req.body;
        const {attribute} = req.body;
        const {value} = req.body;
        //const {data} = req.body;
        var dataRes;
        //const {options} = req.body;
        //const orbitAddress = await orbitdb.determineAddress(name, type);
        try{
            if(_dataBases.hasOwnProperty(name)){
                dataRes = getQuery(_dataBases[name], attribute, operator, value);
            } else{
                _dataBases[name] = await orbitdb.open(await orbitdb.determineAddress(name, 'docstore'));
                console.warn('WARN|',`Database ${name} was not loaded, loading now`);
                dataRes = getQuery(_dataBases[name], attribute, operator, value);
            }
        }catch (error){
            console.error('ERR | in /queryData:', error.message);
            res.status(414).send({
                'info': 'Database does not exist'
            });
        }
        
        res.status(200).send({
            'info': 'Query fetched successfully',
            'data': dataRes
        });
    } catch (error){
        console.error('ERR | in /queryData:', error.message);
        res.status(500).send({
            'info': 'Could not open/query database'
        });
    }
    
});

/**
 * Endpoint to load database
 * @method: POST
 * @body: JSON
 * @param {string} name - The name of the database
 */
app.post('/loadDB', async (req, res) => {
    try{
        const {name} = req.body;
        var dataRes;
        if(OrbitDB.isValidAddress(name)){
            _replicating.push(name);
            console.log('INFO|',`Database ${name} replicating`);
            orbitdb.open(name).then((db) => {
                _replicating.splice(db.name, 1);
                _dataBases[db.dbname] = db;
                console.log('INFO|',`Database ${name} replicated`);
            })
            .catch((error) => {
                if (error.message.includes('context deadline exceeded')){
                    console.error('ERR | failed to replicate. Retrying..');
                    orbitdb.open(name).then((db) => {
                        _replicating.splice(db.name, 1);
                        _dataBases[db.dbname] = db;
                        console.log('INFO|',`Database ${name} replicated`);
                    });
                }
            });
            res.status(200).send({
                'info': 'Database Queued for replication'
            });
            
        }
        else if(_dataBases.hasOwnProperty(name)){
            dataRes = infoDatabase(name);
            res.status(200).send({
                'info': 'Query fetched successfully',
                'data': dataRes
            });
        } else{
            _dataBases[name] = await orbitdb.open(await orbitdb.determineAddress(name, 'docstore'));
            _dataBases[name].events.on('replicated', (address) => {
                console.log('INFO|',`Database ${name} replicated`);
            });
            console.warn('WARN|',`Database ${name} was not loaded, loading now`);
            dataRes = infoDatabase(name);
            res.status(200).send({
                'info': 'Query fetched successfully',
                'data': dataRes
            });
        }
    } catch (error){
        console.error('ERR | in /loadDB:', error.message);
        res.status(500).send({
            'info': 'Could not load database'
        });
    }
    
});

/**
 * Endpoint to test connection
 * @method: POST
 * @body: JSON
 * @param {let} message - The message to echo
 */
app.post('/test', (req, res) => {
    const {message} = req.body;
    res.status(200).send({
        'You typed': message
    })
});


/**
 * Server initialization
 */
const server = app.listen(
    PORT,
    async () => {
        try{
            
            ipfs = create(new URL(`http://${options.ipfsHost}:${options.ipfsPort}`));
            orbitdb = await OrbitDB.createInstance(ipfs, {directory: options.orbitdbDir});
            console.log(`Server is running on port ${PORT}`);
            console.log(`Orbit-db peer public key: ${JSON.stringify(orbitdb.identity, null, 4)}`)
        } catch (error){
            console.error(error);
            server.close();
        }
    }
)