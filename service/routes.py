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
from flask import current_app as app
from service.models import Order, OrderItem
from service.common import status  # HTTP Status Codes
from service.common.order_status import Status
from datetime import datetime, timedelta


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
                    "create": {"method": "POST", "url": "/orders"},
                    "get": {"method": "GET", "url": "/orders/<int:order_id>"},
                    "update": {"method": "PUT", "url": "/orders/<int:order_id>"},
                    "delete": {"method": "DELETE", "url": "/orders/<int:order_id>"},
                },
                "order_items": {
                    "list": {
                        "method": "GET",
                        "url": "/orders/<int:order_id>/orderitems",
                    },
                    "create": {
                        "method": "POST",
                        "url": "/orders/<int:order_id>/orderitems",
                    },
                    "get": {
                        "method": "GET",
                        "url": "/orders/<int:order_id>/orderitems/<int:orderitem_id>",
                    },
                    "update": {
                        "method": "PUT",
                        "url": "/orders/<int:order_id>/orderitems/<int:orderitem_id>",
                    },
                    "delete": {
                        "method": "DELETE",
                        "url": "/orders/<int:order_id>/orderitems/<int:orderitem_id>",
                    },
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

    status_arg = request.args.get("status")
    customer_id = request.args.get("customer_id")
    created_at = request.args.get("created_at")

    query = Order.query

    if status_arg:
        try:
            status_enum = Status[status_arg.upper()]
            query = query.filter(Order.status == status_enum)
        except KeyError:
            abort(
                status.HTTP_400_BAD_REQUEST,  # Use status (HTTP) not http_status
                f"Unknown status '{status_arg}'. Valid statuses: {[s.name for s in Status]}",
            )

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    if created_at:
        try:
            dt = datetime.fromisoformat(created_at)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,  # Use status (HTTP)
                "Invalid date format for created_at. Use ISO 8601 like '2025-10-20' or '2025-10-20T15:30:00'.",
            )

        if len(created_at) <= 10:  # YYYY-MM-DD
            start = datetime(dt.year, dt.month, dt.day)
            end = start + timedelta(days=1)
            query = query.filter(Order.created_at >= start, Order.created_at < end)
        else:
            query = query.filter(Order.created_at == dt)    

    orders = query.all()
    results = [order.serialize() for order in orders]
    return jsonify(results), status.HTTP_200_OK  # Use status (HTTP)

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
    location_url = url_for("get_orders", order_id=order.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update from the json in the body of the request
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
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


######################################################################
# ADD AN ORDERITEM TO AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/orderitems", methods=["POST"])
def create_orderitems(order_id):
    """
    Create an OrderItem on an Order

    This endpoint will add an orderitem to an order
    """
    app.logger.info("Request to create an OrderItem for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an orderitem from the json data
    orderitem = OrderItem()
    orderitem.deserialize(request.get_json())

    # Append the orderitem to the order
    order.orderitem.append(orderitem)
    order.update()

    # Prepare a message to return
    message = orderitem.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_orderitems", order_id=order.id, orderitem_id=orderitem.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


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
# UPDATE AN ORDERITEM
######################################################################
@app.route("/orders/<int:order_id>/orderitems/<int:orderitem_id>", methods=["PUT"])
def update_orderitems(order_id, orderitem_id):
    """
    Update an OrderItem

    This endpoint will update an OrderItem based the body that is posted
    """
    app.logger.info(
        "Request to update OrderItem %s for Order id: %s", (orderitem_id, order_id)
    )
    check_content_type("application/json")

    # See if the orderitem exists and abort if it doesn't
    orderitem = OrderItem.find(orderitem_id)
    if not orderitem:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{orderitem_id}' could not be found.",
        )

    # Update from the json in the body of the request
    orderitem.deserialize(request.get_json())
    orderitem.id = orderitem_id
    orderitem.update()

    return jsonify(orderitem.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDERITEM
######################################################################
@app.route("/orders/<int:order_id>/orderitems/<int:orderitem_id>", methods=["DELETE"])
def delete_orderitems(order_id, orderitem_id):
    """
    Delete an OrderItem

    This endpoint will delete an OrderItem based the id specified in the path
    """
    app.logger.info(
        "Request to delete OrderItem %s for Order id: %s", (orderitem_id, order_id)
    )

    # See if the orderitem exists and delete it if it does
    orderitem = OrderItem.find(orderitem_id)
    if orderitem:
        orderitem.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ORDERITEMS
######################################################################
@app.route("/orders/<int:order_id>/orderitems", methods=["GET"])
def list_orderitems(order_id):
    """Returns all of the OrderItems for an Order"""
    app.logger.info("Request for all OrderItems for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Get the orderitems for the order
    results = [orderitem.serialize() for orderitem in order.orderitem]

    return jsonify(results), status.HTTP_200_OK


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
