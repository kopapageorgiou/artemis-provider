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
        db = await orbitdb.create(name, type, options);
        console.info('INFO|',`Database ${name} created`);
        writeID(name, db.id);
        res.status(200).send({
            'info': 'Database created',
            'database_id': db.id
        });
    } catch (error){
        console.error('ERR | in /createDB:', error.message);
        res.status(500).send({
            'info': 'Database failed to create',
        });
    }
    
});

app.post('/insertData', async (req, res) => {
    try{
        console.log(_dataBases);
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

app.post('/getData', async (req, res) => {
    try{
        console.log(_dataBases);
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

app.post('/test', (req, res) => {
    const {message} = req.body;
    res.status(200).send({
        'You typed': message
    })
});

const server = app.listen(
    PORT,
    async () => {
        try{
            
            ipfs = create(new URL(`http://${options.ipfsHost}:${options.ipfsPort}`));
            orbitdb = await OrbitDB.createInstance(ipfs, {directory: options.orbitdbDir});
            console.log(`Server is running on port ${PORT}`);
            console.log(`Orbit-db peer public key: ${orbitdb.identity.id}`)
        } catch (error){
            console.error(error);
            server.close();
        }
    }
)