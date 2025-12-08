"""
Orders Namespace
"""
from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from service.models import Order, OrderItem
from service.common import status
from service.common.order_status import Status
from datetime import datetime, timedelta

ns = Namespace('orders', description='Order operations')

order_item_model = ns.model('OrderItemModel', {
    'id': fields.Integer(readOnly=True, description='OrderItem ID'),
    'order_id': fields.Integer(required=True, description='Order ID'),
    'product_id': fields.String(required=True, description='Product ID'),
    'price': fields.String(required=True, description='Price'),
    'quantity': fields.String(attribute=lambda x: str(x.quantity), 
                              description='Quantity'),
    'line_amount': fields.String(readOnly=True, description='Line amount')
})

order_model = ns.model('Order', {
    'id': fields.Integer(readOnly=True, description='Order ID'),
    'customer_id': fields.String(required=True, description='Customer ID'),
    'status': fields.String(attribute=lambda x: x.status.name, 
                           enum=[s.name for s in Status], 
                           description='Order status'),
    'total_amount': fields.String(readOnly=True, description='Total amount'),
    'created_at': fields.DateTime(readOnly=True, description='Creation date'),
    'updated_at': fields.DateTime(readOnly=True, description='Last update'),
    'orderitem': fields.List(fields.Nested(order_item_model), description='Order items')
})

create_order_model = ns.model('CreateOrder', {
    'customer_id': fields.String(required=True, description='Customer ID'),
    'status': fields.String(required=True, enum=[s.name for s in Status], description='Order status'),
    'orderitem': fields.List(fields.Nested(order_item_model), required=False, description='Order items')
})

# Query parameter parser
order_parser = reqparse.RequestParser()
order_parser.add_argument('status', type=str, help='Filter by status')
order_parser.add_argument('customer_id', type=str, help='Filter by customer ID')
order_parser.add_argument('created_at', type=str, help='Filter by creation date (ISO format)')

@ns.route('')
class OrderCollection(Resource):
    """Handles list and creation of Orders"""
    
    @ns.doc('list_orders')
    @ns.expect(order_parser)
    @ns.marshal_list_with(order_model)
    def get(self):
        """List all orders with optional filtering"""
        args = order_parser.parse_args()
        status_arg = args.get('status')
        customer_id = args.get('customer_id')
        created_at = args.get('created_at')
        
        query = Order.query
        
        if status_arg:
            try:
                status_enum = Status[status_arg.upper()]
                query = query.filter(Order.status == status_enum)
            except KeyError:
                ns.abort(status.HTTP_400_BAD_REQUEST,
                         f"Unknown status '{status_arg}'. Valid statuses: {[s.name for s in Status]}")
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
            except ValueError:
                ns.abort(status.HTTP_400_BAD_REQUEST,
                         "Invalid date format for created_at. Use ISO 8601.")
            
            if len(created_at) <= 10:  
                start = datetime(dt.year, dt.month, dt.day)
                end = start + timedelta(days=1)
                query = query.filter(Order.created_at >= start, Order.created_at < end)
            else:
                query = query.filter(Order.created_at == dt)
        
        orders = query.all()
        return orders, status.HTTP_200_OK
    
    @ns.doc('create_order')
    @ns.expect(create_order_model)
    @ns.response(status.HTTP_201_CREATED, 'Order created')
    @ns.response(status.HTTP_400_BAD_REQUEST, 'Invalid input')
    @ns.marshal_with(order_model, code=status.HTTP_201_CREATED)
    def post(self):
        """Create a new order"""
        data = request.get_json()
        order = Order()
        order.deserialize(data)
        order.create()
        return order, status.HTTP_201_CREATED, {'Location': f'/api/orders/{order.id}'}

@ns.route('/<int:order_id>')
@ns.param('order_id', 'The Order identifier')
@ns.response(404, 'Order not found')
class OrderResource(Resource):
    """Handles single Order operations"""
    
    @ns.doc('get_order')
    @ns.marshal_with(order_model)
    def get(self, order_id):
        """Retrieve a single order"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' not found")
        return order, status.HTTP_200_OK
    
    @ns.doc('update_order')
    @ns.expect(order_model)
    @ns.response(400, 'Invalid input')
    @ns.marshal_with(order_model)
    def put(self, order_id):
        """Update an order"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' not found")
        
        data = request.get_json()
        order.deserialize(data)
        order.id = order_id
        order.update()
        return order, status.HTTP_200_OK
    
    @ns.doc('delete_order')
    @ns.response(204, 'Order deleted')
    def delete(self, order_id):
        """Delete an order"""
        order = Order.find(order_id)
        if order:
            order.delete()
        return '', status.HTTP_204_NO_CONTENT

@ns.route('/<int:order_id>/cancel')
@ns.param('order_id', 'The Order identifier')
class OrderCancel(Resource):
    """Cancel an order"""
    
    @ns.doc('cancel_order')
    @ns.response(200, 'Order cancelled')
    @ns.response(404, 'Order not found')
    @ns.response(409, 'Order cannot be cancelled')
    @ns.marshal_with(order_model)
    def put(self, order_id):
        """Cancel an order"""
        order = Order.find(order_id)
        if not order:
            ns.abort(status.HTTP_404_NOT_FOUND, f"Order {order_id} not found")
        
        if order.status != Status.CREATED:
            ns.abort(status.HTTP_409_CONFLICT, 
                    f"Cannot cancel order in status {order.status.name}")
        
        order.status = Status.CANCELED
        order.update()
        return order, status.HTTP_200_OK
