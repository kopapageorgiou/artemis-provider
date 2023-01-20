from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('id', type=int)
parser.add_argument('timestamp', type=int)
parser.add_argument('temperature', type=float)
parser.add_argument('ids', type=tuple)
parser.add_argument('from_timestamp', type=int)
parser.add_argument('to_timestamp', type=int)
parser.add_argument('token', type=str)

class write(Resource):
    
    def post(self):
        try:
            args = parser.parse_args()
            
            ident = args['id']
            timestamp = args['timestamp']
            temperature = args['temperature']
            token = args['token']

        except:
            print("Attributes are invalid")

class read(Resource):

    def post(self):

        try:
            args = parser.parse_args()

            ids = args['ids']
            from_timestamp = args['from_timestamp']
            to_timestamp = args['to_timestamp']
            token = args['token']
        except:
            print("Attributes are invalid")

def get_token(Reseource):
    
    def post(self):
        pass

api.add_resource(write, "/writedata")
api.add_resource(read, "/readdata")
api.add_resource(get_token, "/get_token")

if __name__ == "__main__":
    app.run(debug=True)