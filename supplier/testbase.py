from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
try:
    session = cluster.connect('mkeyspace')
except Exception as e:
    session = cluster.connect()
    query = '''CREATE KEYSPACE mKeySpace WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 1}
    AND durable_writes = true;'''
    session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS clients (
    client_id text PRIMARY KEY,
    client_name text,
    ) WITH comment='Clients information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS gateways (
    gateway_id text PRIMARY KEY,
    gateway_description text,
    vehicle_id text,
    client_id text,
    ) WITH comment='Gateways information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS sensors (
    sensor_id text PRIMARY KEY,
    sensor_type text,
    gateway_id text,
    ) WITH comment='Sensors information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS measurements (
    measurement_id int PRIMARY KEY,
    measurement_value int,
    measurement_time timestamp,
    measurement_location text,
    current_stop_id text,
    sensor_id text,
    ) WITH comment='Measurements information'
''' #! STEP 2
session.execute(query=query)
session.shutdown()
#query= '''SELECT * FROM monkeySpecies''' #! STEP 3
#rows = 
#print([row for row in rows])