from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
try:
    session = cluster.connect()
    query = '''CREATE KEYSPACE mKeySpace WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 1}
    AND durable_writes = true;'''
    session.execute(query=query)
    #session = cluster.connect("mkeyspace")
except Exception as e:
    print(e)
session = cluster.connect("mkeyspace")
    

query = '''
    CREATE TABLE IF NOT EXISTS clients (
    client_id int PRIMARY KEY,
    client_name text,
    ) WITH comment='Clients information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS gateways (
    gateway_id int PRIMARY KEY,
    gateway_description text,
    vehicle_id text,
    client_id int,
    ) WITH comment='Gateways information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS sensors (
    sensor_id text PRIMARY KEY,
    sensor_type text,
    gateway_id int,
    ) WITH comment='Sensors information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS measurements (
    measurement_id int,
    measurement_value float,
    measurement_time timestamp,
    measurement_location text,
    sensor_id text,
    PRIMARY KEY (sensor_id, measurement_time, measurement_id)
    ) WITH comment='Measurements information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS commitments (
    hash_string text PRIMARY KEY,
    signature text,
    gateway_id text,
    begin_t timestamp,
    end_t timestamp,
    ) WITH comment='Commitments information'
''' #! STEP 2

session.execute(query=query)

# query = '''
#     CREATE TABLE IF NOT EXISTS measurements2 (
#     measurement_id int,
#     measurement_value float,
#     measurement_time timestamp,
#     measurement_location text,
#     sensor_id text,
#     PRIMARY KEY (sensor_id, measurement_time)
#     ) WITH comment='Measurements information'
# ''' #! STEP 2
# session.execute(query=query)
session.shutdown()
#query= '''SELECT * FROM monkeySpecies''' #! STEP 3
#rows = 
#print([row for row in rows])