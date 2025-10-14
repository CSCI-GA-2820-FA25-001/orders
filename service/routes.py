######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order and OrderItem Service

This microservice handles the lifecycle of Orders and OrderItems
"""
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, OrderItem, Status
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Order REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
            endpoints={
                "orders": {
                    "list": {"method": "GET", "url": "/orders"},
                    # Todo: uncomment once the endpoint is implemented and tested
                    #                "create": {"method":"POST", "url": "/orders"},
                    #                "get":    {"method": "GET", "url": "/orders/<int:order_id>"},
                    #                "update": {"method": "PUT", "url": "/orders/<int:order_id>"},
                    #                "delete": {"method": "DELETE", "url": "/orders/<int:order_id>"}
                },
                "order_items": {
                    # Todo: uncomment once the endpoint is implemented and tested
                    #                "list":   {"method": "GET","url": "/orders/<int:order_id>/items"},
                    #                "create": {"method": "POST", "url": "/orders/<int:order_id>/items"},
                    #                "get":    {"method": "GET", "url": "/orders/<int:order_id>/items/<int:item_id>"},
                    #                "update": {"method": "PUT", "url": "/orders/<int:order_id>/items/<int:item_id>"},
                    #                "delete": {"method": "DELETE", "url": "/orders/<int:order_id>/items/<int:item_id>"}
                },
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for Order list")
    orders = []

    # Process the query string if any
    customer_id = request.args.get("customer_id")
    if customer_id:
        orders = Order.find_by_customer_id(customer_id)
    else:
        orders = Order.all()

    # Return as an array of dictionaries
    results = [order.serialize() for order in orders]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order

    This endpoint will return an Order based on it's id
    """
    app.logger.info("Request for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # Create the order
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()
    # Todo; uncomment this code when get_orders is implemented
    # location_url = url_for("get_orders", order_id=order.id, _external=True)
    location_url = "unknown"

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# DELETE An ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to Delete an order with id [%s]", order_id)

    # Delete the Order if it exists
    order = Order.find(order_id)
    if order:
        app.logger.info("Order with ID: %d found.", order.id)
        order.delete()

    app.logger.info("Order with ID: %d delete complete.", order_id)
    return {}, status.HTTP_204_NO_CONTENT
    
#############################################################################
# RETRIEVE AN ORDERITEM FROM ORDER
######################################################################
@app.route("/orders/<int:order_id>/orderitems/<int:orderitem_id>", methods=["GET"])
def get_orderitems(order_id, orderitem_id):
    """
    Get an OrderItem

    This endpoint returns just an orderitem
    """
    app.logger.info(
        "Request to retrieve OrderItem %s for Order id: %s", orderitem_id, order_id
    )

    # See if the orderitem exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # See if the orderitem exists and abort if it doesn't
    orderitem = OrderItem.find(orderitem_id)
    if not orderitem:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"OrderItem with id '{orderitem_id}' could not be found.",
        )
    if orderitem.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"OrderItem '{orderitem_id}' does not belong to Order '{order_id}'.",
        )

    return jsonify(orderitem.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
