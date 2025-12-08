"""
OrderItems Namespace
"""
from flask_restx import Namespace, Resource, fields
from flask import request
from service.models import Order, OrderItem
from service.common import status
from .orders import order_item_model

# Create namespace
ns = Namespace('orderitems', description='OrderItem operations', path='/orders/<int:order_id>/orderitems')


create_order_item_model = ns.model('CreateOrderItem', {
    'product_id': fields.String(required=True, description='Product ID'),
    'price': fields.String(required=True, description='Price'),
    'quantity': fields.Integer(required=True, description='Quantity')
})


@ns.route('')
@ns.param('order_id', 'The Order identifier')
class OrderItemCollection(Resource):
    """Handles list and creation of OrderItems for an Order"""

    @ns.doc('list_orderitems')
    @ns.response(404, 'Order not found')
    @ns.marshal_list_with(order_item_model)
    def get(self, order_id):
        """List all order items for an order"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' could not be found.")
        return order.orderitem, status.HTTP_200_OK

    @ns.doc('create_orderitem')
    @ns.expect(create_order_item_model)
    @ns.response(201, 'OrderItem created')
    @ns.response(400, 'Invalid input')
    @ns.response(404, 'Order not found')
    @ns.marshal_with(order_item_model, code=201)
    def post(self, order_id):
        """Add an order item to an order"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' could not be found.")

        data = request.get_json()
        orderitem = OrderItem()
        orderitem.deserialize({**data, 'order_id': order_id})

        order.orderitem.append(orderitem)
        order.update()

        return orderitem, status.HTTP_201_CREATED, {'Location': f'/api/orders/{order_id}/orderitems/{orderitem.id}'}


@ns.route('/<int:orderitem_id>')
@ns.param('order_id', 'The Order identifier')
@ns.param('orderitem_id', 'The OrderItem identifier')
class OrderItemResource(Resource):
    """Handles single OrderItem operations"""

    @ns.doc('get_orderitem')
    @ns.response(404, 'OrderItem not found')
    @ns.marshal_with(order_item_model)
    def get(self, order_id, orderitem_id):
        """Get a specific order item"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' could not be found.")

        orderitem = OrderItem.find(orderitem_id)
        if not orderitem:
            ns.abort(status.HTTP_404_NOT_FOUND, f"OrderItem with id '{orderitem_id}' could not be found.")

        if orderitem.order_id != order_id:
            ns.abort(status.HTTP_404_NOT_FOUND, f"OrderItem '{orderitem_id}' does not belong to Order '{order_id}'.")

        return orderitem, status.HTTP_200_OK

    @ns.doc('update_orderitem')
    @ns.expect(order_item_model)
    @ns.response(400, 'Invalid input')
    @ns.response(404, 'OrderItem not found')
    @ns.marshal_with(order_item_model)
    def put(self, order_id, orderitem_id):
        """Update an order item"""
        orderitem = OrderItem.find(orderitem_id)
        if not orderitem:
            ns.abort(status.HTTP_404_NOT_FOUND, f"OrderItem with id '{orderitem_id}' could not be found.")

        data = request.get_json()
        orderitem.deserialize({**data, 'order_id': order_id})
        orderitem.id = orderitem_id
        orderitem.update()

        return orderitem, status.HTTP_200_OK

    @ns.doc('delete_orderitem')
    @ns.response(204, 'OrderItem deleted')
    @ns.response(404, 'OrderItem not found')
    def delete(self, order_id, orderitem_id):
        """Delete an order item"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' could not be found.")

        orderitem = OrderItem.find(orderitem_id)

        if not orderitem:
            return '', status.HTTP_204_NO_CONTENT

        if orderitem.order_id != order_id:
            ns.abort(status.HTTP_404_NOT_FOUND, f"OrderItem '{orderitem_id}' does not belong to Order '{order_id}'.")

        orderitem.delete()
        return '', status.HTTP_204_NO_CONTENT
