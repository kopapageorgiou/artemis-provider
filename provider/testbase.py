from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect('mkeyspace') #! STEP 1
#session = cluster.connect('mkeyspace') #!STEP 2,3

query = '''CREATE KEYSPACE mKeySpace WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 1} #! STEP 1
AND durable_writes = true;'''

# query = '''
#      CREATE TABLE monkeySpecies (
#      species text PRIMARY KEY,
#      common_name text,
#      population varint,
#      average_size int
#  ) WITH comment='Important biological records'
# ''' #! STEP 2

#query= '''SELECT * FROM monkeySpecies''' #! STEP 3
rows = session.execute(query=query)
print([row for row in rows])