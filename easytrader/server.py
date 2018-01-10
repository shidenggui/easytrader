from flask import Flask, request, jsonify

from . import api

app = Flask(__name__)

global_store = {}


@app.route('/prepare', methods=['POST'])
def post_prepare():
    json_data = request.get_json(force=True)

    try:
        user = api.use(json_data.pop('broker'))
        user.prepare(**json_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    global_store['user'] = user
    return jsonify({'msg': 'login success'}), 201


@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        user = global_store['user']
        balance = user.balance
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(balance), 200


@app.route('/position', methods=['GET'])
def get_position():
    try:
        user = global_store['user']
        position = user.position
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(position), 200


@app.route('/auto_ipo', methods=['GET'])
def get_auto_ipo():
    try:
        user = global_store['user']
        res = user.auto_ipo()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(res), 200


@app.route('/today_entrusts', methods=['GET'])
def get_today_entrusts():
    try:
        user = global_store['user']
        today_entrusts = user.today_entrusts
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(today_entrusts), 200


@app.route('/today_trades', methods=['GET'])
def get_today_trades():
    try:
        user = global_store['user']
        today_trades = user.today_trades
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(today_trades), 200


@app.route('/cancel_entrusts', methods=['GET'])
def get_cancel_entrusts():
    try:
        user = global_store['user']
        cancel_entrusts = user.cancel_entrusts
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(cancel_entrusts), 200


@app.route('/buy', methods=['POST'])
def post_buy():
    json_data = request.get_json(force=True)
    try:
        user = global_store['user']
        res = user.buy(**json_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(res), 201


@app.route('/sell', methods=['POST'])
def post_sell():
    json_data = request.get_json(force=True)
    try:
        user = global_store['user']
        res = user.sell(**json_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(res), 201


@app.route('/cancel_entrust', methods=['POST'])
def post_cancel_entrust():
    json_data = request.get_json(force=True)
    try:
        user = global_store['user']
        res = user.cancel_entrust(**json_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(res), 201


@app.route('/exit', methods=['GET'])
def get_exit():
    try:
        user = global_store['user']
        user.exit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'msg': 'exit success'}), 200


def run(port=1430):
    app.run(host='0.0.0.0', port=port)
