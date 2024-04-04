from flask import Flask
import json
from ORM_models import create_object, info_user
app = Flask(__name__)


@app.route('/')
@app.route('/api/apikey123/create_obj/<string:dat>', methods=['POST'])
def create_obj(dat):
    data = json.loads(dat)
    create_object(data["name"], data["des"])
    return data["name"]

@app.route('/api/apikey123/get_info_user/<string:email>')
def get_info_user(email):
    return info_user(email)


@app.route('/index')
def index2():
    return "aaaaa"

if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
