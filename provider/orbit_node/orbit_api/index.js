import OrbitDB from 'orbit-db'
import { create } from 'ipfs-http-client'
import express from 'express';
import fs from 'fs';
const app = express();
const PORT = 3000;

const ipfs = create(new URL('http://127.0.0.1:5001'));
var orbitdb 

var _dataBases = {};
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
        const {name} = req.body;
        const {type} = req.body;
        const {data} = req.body;
        //const {options} = req.body;
        //const orbitAddress = await orbitdb.determineAddress(name, type);
        try{
            if(_dataBases.hasOwnProperty(name)){
                for (var key in data){
                    if (data.hasOwnProperty(key)){
                        _dataBases[name].put({_id: key, name: data[key]});
                    }
                }
            } else{
                _dataBases[name] = await orbitdb.open(await orbitdb.determineAddress(name, type));
                console.warn('WARN|',`Database ${name} was not loaded, loading now`);
            }
        }catch (error){
            _dataBases[name] = await orbitdb.open(name, {
                create: true,
                type: type,
                overwrite: false,
                replicate: true
            });
            console.warn('WARN|',`Database ${name} not found, creating new database`);
        }
        for (var key in data){
            if (data.hasOwnProperty(key)){
                _dataBases[name].put({_id: key, name: data[key]});
            }
        }
        res.status(200).send({
            'info': 'Data inserted successfully',
            'data_base': infoDatabase(name)
        });
    } catch (error){
        console.error('ERR | in /insertData:', error.message);
        res.status(500).send({
            'info': 'Could not open/store data to database'
        });
    }
    
});

app.post('/getData', async (req, res) => {
    try{
        const {name} = req.body;
        const {type} = req.body;
        const {data} = req.body;
        //const {options} = req.body;
        //const orbitAddress = await orbitdb.determineAddress(name, type);
        try{
            if(_dataBases.hasOwnProperty(name)){
                for (var key in data){
                    if (data.hasOwnProperty(key)){
                        _dataBases[name].put({_id: key, name: data[key]});
                    }
                }
            } else{
                _dataBases[name] = await orbitdb.open(await orbitdb.determineAddress(name, type));
                console.warn('WARN|',`Database ${name} was not loaded, loading now`);
            }
        }catch (error){
            console.error('ERR | in /getData:', error.message);
            res.status(414).send({
                'info': 'Database does not exist'
            });
        }
        var dataRes = _dataBases[name].get('');
        res.status(200).send({
            'info': 'Data inserted successfully',
            'data': dataRes
        });
    } catch (error){
        console.error('ERR | in /getData:', error.message);
        res.status(500).send({
            'info': 'Could not open/store data to database'
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
            orbitdb = await OrbitDB.createInstance(ipfs);
            console.log(`Server is running on port ${PORT}`);
        } catch (error){
            console.error(error);
            server.close();
        }
    }
)