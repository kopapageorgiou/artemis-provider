from Orbitdbapi import OrbitdbAPI
import sys

orbitdb = OrbitdbAPI(orbithost='127.0.0.1', port=3000)
db = orbitdb.load(dbname='test-base1')
# print(db, file=sys.stderr)
res = db.insert(dbname='test-base1', data={"key": 2, "name": "testName2"})
print(res, file=sys.stderr)
res = db.query(dbname='test-base1', query={"attribute": "name", "operator": "eq", "value": "testName"})
print(res, file=sys.stderr)
# res = db.getAll(dbname='test-base1')
# print(res, file=sys.stderr)