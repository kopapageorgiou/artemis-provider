import requests
import sys
class OrbitdbAPI():
    def __init__(self, orbithost: str, port: int=3000) -> None:
        self.BASE_URL = f"http://{orbithost}:{str(port)}"
        #self.operators = ['eq', 'ne', 'gt', 'gte', 'lt', 'lte']
    
    def load(self, dbname: str) -> dict:
        response = requests.post(self.BASE_URL+'/loadDB', json={"name": dbname}).json()

        #self.key = response['data_base']['options']['indexBy']
        return _dataBase(response['data'], self.BASE_URL)
    
    
    # def closeDB(self, dbname: str) -> dict:
    #     self.key = None

class _dataBase():
    def __init__(self, info: dict, baseURL: str) -> None:
        self.BASE_URL = baseURL
        self.info = info
        self.dbname = self.info['dbname']
        self.key = self.info['options']['indexBy']
        self.operators = ['eq', 'ne', 'gt', 'gte', 'lt', 'lte']
    
    # def __call__(self):
    #     return self.info
    
    def insert(self, data: dict) -> dict:
        assert 'key' in data.keys(), "Data must contain an attribute named key"
        attr = {}
        for key in data.keys():
            if key == 'key':
                attr[self.key] = data[key]
            else:
                attr[key] = data[key]

        return requests.post(self.BASE_URL+'/insertMeasurements', json={"name": self.dbname, "data": attr}).json()
    
    def query(self, query: dict) -> dict:
        #assert 'key' in query, "Query must contain a key attribute"
        assert 'operator' in query.keys(), "Query must contain an attribute named operator"
        assert query['operator'] in self.operators, "Operator must be one of the following: " + str(self.operators)
        assert 'attribute' in query.keys(), "Query must contain an attribute named attribute"
        assert 'value' in query.keys(), "Query must contain an attribute named value"

        return requests.post(self.BASE_URL+'/queryData', json={
            "name": self.dbname,
            "attribute": query['attribute'],
            "operator": query['operator'],
            "value": query['value']}).json()
    
    def getAll(self) -> dict:
        return requests.post(self.BASE_URL+'/getData', json={"name": self.dbname}).json()

