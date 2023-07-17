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
    CREATE TABLE IF NOT EXISTS batches (
    batch_id integer PRIMARY KEY,
    ) WITH comment='Batches information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS products (
    product_id text PRIMARY KEY,
    batch_id integer,
    order_id text
    ) WITH comment='Products information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS stops (
    customer_id text PRIMARY KEY,
    stop_id text,
    location text
    ) WITH comment='Stops information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS customers (
    customer_id int PRIMARY KEY,
    customer_name text
    ) WITH comment='Customers information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id str PRIMARY KEY
    ) WITH comment='Vehicles information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS shipments (
    shipment_id str PRIMARY KEY,
    shipment_date date,
    vehicle_id str
    ) WITH comment='Shipments information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS orders (
    order_id str PRIMARY KEY,
    customer_id str,
    stop_id str,
    shipment_id str
    ) WITH comment='Orders information'
''' #! STEP 2
session.execute(query=query)

session.shutdown()
#query= '''SELECT * FROM monkeySpecies''' #! STEP 3
#rows = 
#print([row for row in rows])