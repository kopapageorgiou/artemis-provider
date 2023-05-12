import OrbitDB from 'orbit-db'
import AccessControllers from 'orbit-db-access-controllers'
import AccessController from 'orbit-db-access-controllers/interface'
import { create } from 'ipfs-http-client'
import { program } from 'commander';
import express from 'express';
import fs from 'fs';

class CustomAccessController extends AccessController{
    constructor(){

    }
    static get type () {return 'actype'}
    
    canAppend(entry, identityProvider){
        return true;
    }

    canPut(key, entry, identityProvider){
        return false;
    }

    canDelete(key, entry, identityProvider){
        return false;
    }
}

AccessControllers.addAccessController({AccessController: CustomAccessController})
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

app.post('/createDB', async (req, res) => {
    try{
        const {name} = req.body;
        const {type} = req.body;
        const {options} = req.body;
        _dataBases[name] = await orbitdb.create(name, type, options);
        setController(_dataBases[name]);

        console.info('INFO|',`Database ${name} created`);
        writeID(name, _dataBases[name].id);
        res.status(200).send({
            'info': 'Database created',
            'database_id': _dataBases[name].id
        });
    } catch (error){
        console.error('ERR | in /createDB:', error.message);
        res.status(500).send({
            'info': 'Database failed to create',
        });
    }
    
});

app.post('/addPeer', async (req, res) => {
    const {peerIdentity} = req.body;
    try{
            _dataBases['shared.orders'] = await orbitdb.open(await orbitdb.determineAddress('shared.orders', 'docstore'), {
                accessController: {
                    type: 'orbitdb',
                    write: [peerIdentity]
                }
            });
            // }).then(async (db)=>{
            //     const accessControl = db.access._write

            //     // Step 3: Modify the access control configuration
            //     accessControl.push(peerIdentity)

            //     // Step 4: Save and apply the updated access control configuration
            //     db.access._write= accessControl

            //     // Step 5: Grant write access to the new peer
            //     await db.access.grant('write', peerIdentity)

            //     // Step 6: Save and apply the access control changes
            //     await db.access.write.save()
            // });
            await _dataBases['shared.orders'].access.grant('write', peerIdentity);
            console.info('INFO|',`Database shared.orders was loaded with write access for ${peerIdentity}`);
        
        res.status(200).send({
            'info': 'Peer added successfully'
        });
    }catch (error){
        console.error('ERR | in /addPeer:', error);
        res.status(414).send({
            'info': 'Database does not exist'
        });
    }
});

app.post('/insertData', async (req, res) => {
    try{
        const {name} = req.body;
        const {data} = req.body;
        _dataBases[name].put(data, { pin: true });
        res.status(200).send({
            'info': 'Data inserted successfully',
            'data_base': infoDatabase(name)
        });
    } catch (error){
        console.error('ERR | in /insertData:', error.message);
        res.status(500).send({
            'info': 'Could not store data to database'
        });
    }
    
});

/**
 * Endpoint to insert measurements in shared databases
 * @method: POST
 * @body: JSON
 * @param {let} order_id - The order id concerns the measurement
 * @param {let} measurement_id - The measurement id to register
 * @param {let} sensor_id - The sensor id that got the measurements
 * @param {int} enc_measurement_value - The measurement value to register
 * @param {let} enc_measurement_time - The timestamp that sensor got the measurement
 * @param {let} enc_measurement_location - The location that sensor got the measurement
 * @param {let} abe_enc_key - The encrypted symmetric key
 */
app.post('/insertMeasurements', async (req, res) => {
    try{
        const {order_id} = req.body;
        const {measurement_id} = req.body;
        const {sensor_id} = req.body;
        const {enc_measurement_value} = req.body;
        const {enc_measurement_time} = req.body;
        const {enc_measurement_location} = req.body;
        const {abe_enc_key} = req.body;

        let temp = _dataBases['shared.measurements'].get(measurement_id);
        if (temp.length != 0 && temp[0].sensor_id === sensor_id){
            throw new Error('Measurement already exists');
        }

        _dataBases['shared.measurements'].put({measurement_id: measurement_id,
                                            sensor_id: sensor_id,
                                            enc_measurement_value: enc_measurement_value,
                                            enc_measurement_time: enc_measurement_time,
                                            enc_measurement_location: enc_measurement_location,
                                            abe_enc_key: abe_enc_key});
        

        temp = _dataBases['shared.ordersMeasurements'].get(order_id);
        if (temp.length != 0 && temp[0].measurement_id === measurement_id){
            throw new Error('Measurement already exists');
        }

        _dataBases['shared.ordersMeasurements'].put({order_id: order_id,
                                                    measurement_id: measurement_id});

        res.status(200).send({
            'info': 'Data inserted successfully',
            'data_base': infoDatabase('shared.measurements')
        });


    }
    catch (error){
        console.error('ERR | in /insertMeasurements:', error.message);
        res.status(500).send({
            'info': 'Could not store data to database'
        });
    }
});

app.post('/getData', async (req, res) => {
    try{
        const {name} = req.body;
        //const {data} = req.body;
        var dataRes;
        //const {options} = req.body;
        //const orbitAddress = await orbitdb.determineAddress(name, type);
        dataRes = _dataBases[name].get('');
        res.status(200).send({
            'info': 'Data inserted successfully',
            'data': dataRes
        });
    } catch (error){
        console.error('ERR | in /getData:', error.message);
        res.status(500).send({
            'info': 'Could not get data from database'
        });
    }
    
});

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
                // for (var key in data){
                //     if (data.hasOwnProperty(key)){
                //         dataRes = _dataBases[name].get('');
                //     }
                // }
            } else{
                _dataBases[name] = orbitdb.open(await orbitdb.determineAddress(name, 'docstore')).then(()=>{
                    setController(_dataBases[name]);
                });
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

app.post('/loadDB', async (req, res) => {
    try{
        const {name} = req.body;
        var dataRes;
        //const {options} = req.body;
        //const orbitAddress = await orbitdb.determineAddress(name, type);
        try{
            if(OrbitDB.isValidAddress(name)){
                _replicating.push(name);
                console.log('INFO|',`Database ${name} replicating`);
                orbitdb.open(name).then((db) => {
                    _replicating.splice(db.name, 1);
                    _dataBases[db.dbname] = db;
                //var db = await orbitdb.open(name);
                    //_dataBases[db.dbname] = db;
                    //_dataBases[db.dbname].events.on('replicated', (address) => {
                    console.log('INFO|',`Database ${name} replicated`);
                })
                .catch((error) => {
                    if (error.message.includes('context deadline exceeded')){
                        console.error('ERR | failed to replicate. Retrying..');
                        orbitdb.open(name).then((db) => {
                            _replicating.splice(db.name, 1);
                            _dataBases[db.dbname] = db;
                        //var db = await orbitdb.open(name);
                            //_dataBases[db.dbname] = db;
                            //_dataBases[db.dbname].events.on('replicated', (address) => {
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
                    'data': _dataBases[name]
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
        }catch (error){
            _dataBases[name] = await orbitdb.open(name, {
                create: true,
                type: 'docstore',
                overwrite: false,
                replicate: true
            });
            console.warn('WARN|',`Database ${name} not found, creating new database`);
            dataRes = infoDatabase(name);
            res.status(200).send({
                    'info': 'Query fetched successfully',
                    'data': dataRes
                });
        }
        
        // res.status(200).send({
        //     'info': 'Query fetched successfully',
        //     'data': dataRes
        // });
    } catch (error){
        console.error('ERR | in /loadDB:', error.message);
        res.status(500).send({
            'info': 'Could not create or load database'
        });
    }
    
});
app.post('/initDBs', (req, res) => {
    initDBs();
    res.status(200).send({
        'info': 'Databases initialized'
    });
});
const server = app.listen(
    PORT,
    async () => {
        try{
            
            ipfs = create(new URL(`http://${options.ipfsHost}:${options.ipfsPort}`));
            orbitdb = await OrbitDB.createInstance(ipfs, {directory: options.orbitdbDir, AccessControllers: AccessControllers});
            console.log(`Server is running on port ${PORT}`);
            console.log(`Orbit-db peer public key: ${orbitdb.identity.publicKey}`)
        } catch (error){
            console.error(error);
            server.close();
        }
    }
)

async function setController(db){
    await db.access.grant('write', db.identity.id);
    await db.access.load();// Load access controller state
    db.access.write.accessController = new CustomAccessController();
    db.access.write.save(); // Save access controller state
}

function initDBs(){
    const db_names = ['shared.orders', 'shared.ordersMeasurements', 'shared.measurements']

    try{
        try{
            db_names.forEach(async db_name => {
                if (db_name === 'shared.orders'){
                    _dataBases[db_name] = await orbitdb.create(db_name, 'docstore',{
                        overwrite: false,
                        replicate: true,
                        indexBy: 'order_id',                       
                        accessController:{
                            type: 'orbitdb',
                            write: []
                        }
                    });
                } 
                else{
                    _dataBases[db_name] = await orbitdb.create(db_name, 'docstore',{
                        overwrite: false,
                        replicate: true,
                        indexBy: ((db_name === 'shared.ordersMeasurements') ? 'order_id' : 'measurement_id'),                       
                        accessController:{
                            type: 'orbitdb',
                            write: []
                        }
                    });
                }
                console.info('INFO|',`${db_name} initialized with id: ${infoDatabase(db_name).id}`);
            })
        }
        catch (error){
            db_names.forEach(async db_name => {
                if (db_name === 'shared.orders'){
                    _dataBases[db_name] = await orbitdb.open(db_name, {
                        create: true,
                        type: 'docstore',
                        overwrite: false,
                        replicate: true,
                        accessController: {
                            type: 'orbitdb',
                            write: [null]
                        }
                    });
                }
                else{
                    _dataBases[db_name] = await orbitdb.open(db_name, {
                        create: true,
                        type: 'docstore',
                        overwrite: false,
                        replicate: true
                    });
                }
                console.info('INFO|',`${db_name} id: ${infoDatabase(db_name).id}`);
            
            });
        }
    }
    catch (error){
        console.error('ERR |',`${error.message}`);
    }
}