from flask import Flask, jsonify, request

app = Flask(__name__)

products = []
customers = []
orders = []

# Product Class
class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock
        }

# Customer Class
class Customer:
    def __init__(self, customer_id, name, email):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.cart = Cart()

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'cart': self.cart.to_dict()
        }

# Cart Class
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        self.items.append({'product': product.to_dict(), 'quantity': quantity})

    def view_cart(self):
        return self.items

    def clear_cart(self):
        self.items = []

    def calculate_total(self):
        return sum(item['product']['price'] * item['quantity'] for item in self.items)

    def to_dict(self):
        return {
            'items': self.items,
            'total': self.calculate_total()
        }

# Order Class
class Order:
    def __init__(self, order_id, customer, items, total):
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.total = total

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer': self.customer.to_dict(),
            'items': self.items,
            'total': self.total
        }


@app.route('/products', methods=['GET'])
def get_products():
    return jsonify([product.to_dict() for product in products])

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(len(products) + 1, data['name'], data['price'], data['stock'])
    products.append(new_product)
    return jsonify(new_product.to_dict()), 201

@app.route('/customers', methods=['GET'])
def get_customers():
    return jsonify([customer.to_dict() for customer in customers])

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    new_customer = Customer(len(customers) + 1, data['name'], data['email'])
    customers.append(new_customer)
    return jsonify(new_customer.to_dict()), 201

@app.route('/customers/<int:customer_id>/cart', methods=['POST'])
def add_to_cart(customer_id):
    customer = next((c for c in customers if c.customer_id == customer_id), None)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    data = request.get_json()
    product = next((p for p in products if p.product_id == data['product_id']), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    customer.cart.add_item(product, data['quantity'])
    return jsonify(customer.cart.to_dict()), 200

@app.route('/customers/<int:customer_id>/cart', methods=['GET'])
def view_cart(customer_id):
    customer = next((c for c in customers if c.customer_id == customer_id), None)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(customer.cart.to_dict())

@app.route('/customers/<int:customer_id>/checkout', methods=['POST'])
def checkout(customer_id):
    customer = next((c for c in customers if c.customer_id == customer_id), None)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    if not customer.cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    new_order = Order(len(orders) + 1, customer, customer.cart.view_cart(), customer.cart.calculate_total())
    orders.append(new_order)
    customer.cart.clear_cart()
    return jsonify(new_order.to_dict()), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify([order.to_dict() for order in orders])

if __name__ == '__main__':
    app.run(debug=True)
