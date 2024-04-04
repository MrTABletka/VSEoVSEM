from flask import Flask
import json
from ORM_models import create_object
app = Flask(__name__)


@app.route('/')
@app.route('/api/create_obj/apikey123/<string:dat>', methods=['POST'])
def index(dat):
    data = json.loads(dat)
    create_object(data["name"], data["des"])
    return data["name"]


@app.route('/index')
def index2():
    return "aaaaa"

@app.route('/abc')
def index3():
    return "bbbbb"

if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
