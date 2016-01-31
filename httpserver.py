from __future__ import print_function
from flask import Flask, request, jsonify
import anyjson as json

import easytrader

app = Flask(__name__)
user = None


@app.route('/login')
def login():
    global user
    args = request.args
    user = easytrader.use(args['use'])
    user.prepare(args['prepare'])
    return jsonify({'message': 'login ok'})


@app.route('/call')
def do():
    global user
    target = request.args.get('func')
    params_str = request.args.get('params', None)

    if params_str:
        params = params_str.split(',')
        result = getattr(user, target)(**params)
    else:
        result = getattr(user, target)
    return json.dumps(result)


if __name__ == '__main__':
    app.run(debug=True)
