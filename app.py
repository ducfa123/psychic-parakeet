from flask import Flask, request, jsonify,render_template,request, redirect, url_for
import redis
import json

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0,password = '123456duc',decode_responses=True)
ORDER_KEY_PREFIX = "order:"

class Order:
    def __init__(self, order_id, product_name, quantity, price):
        self.order_id = order_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price

class OrderManager:
    def __init__(self):
        pass

    def add_order(self, order):
        redis_client.set(ORDER_KEY_PREFIX + str(order.order_id), json.dumps(vars(order)))

    def update_order(self, order_id, new_order):
        key = ORDER_KEY_PREFIX + str(order_id)
        if redis_client.exists(key):
            redis_client.set(key, json.dumps(vars(new_order)))
            return True
        return False

    def delete_order(self, order_id):
        redis_client.delete(ORDER_KEY_PREFIX + str(order_id))

    def get_order(self, order_id):
        order_data = redis_client.get(ORDER_KEY_PREFIX + str(order_id))
        if order_data:
            order_json = json.loads(order_data)
            return Order(**order_json)
        return None

    def get_order_list(self):
        order_keys = redis_client.keys(ORDER_KEY_PREFIX + "*")
        order_list = [json.loads(redis_client.get(key)) for key in order_keys]
        return order_list

order_manager = OrderManager()

@app.route('/api/orders', methods=['GET'])
def get_orders():
    order_list_data = order_manager.get_order_list() 
    return render_template('index.html', order_list=order_list_data)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = order_manager.get_order(order_id)
    if order:
        return jsonify(vars(order))
    return jsonify({'message': 'Order not found'}), 404

#them
@app.route('/api/orders/add', methods=['GET'])
def add_order_form():
    return render_template('add_order.html')
@app.route('/api/orders/add', methods=['POST'])
def add_order():
    # Extract form data
    product_name = request.form.get('product_name')
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price'))
    order_id = len(order_manager.get_order_list()) + 1

    new_order = Order(order_id, product_name, quantity, price)

    order_manager.add_order(new_order)

    return redirect(url_for('get_orders'))
#=================================================================
# sua 
@app.route('/api/orders/edit/<int:order_id>', methods=['GET'])
def edit_order(order_id):
    order = order_manager.get_order(order_id)
    return render_template('edit_order.html', order=order)

@app.route('/api/orders/update', methods=['POST'])
def update_order():
    order_id = int(request.form.get('order_id'))
    product_name = request.form.get('product_name')
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price'))

    updated_order = Order(order_id, product_name, quantity, price)

    if order_manager.update_order(order_id, updated_order):
        return redirect(url_for('get_orders'))
    else:
        return "Order not found or could not be updated", 404
#====================================================================
#delete
@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order_manager.delete_order(order_id)
    return jsonify({'message': 'Order deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

