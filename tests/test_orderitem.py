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
Test cases for OrderItem Model
"""

# pylint: disable=duplicate-code

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, OrderItem, DataValidationError, db
from tests.factories import OrderFactory, OrderItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  O R D E R I T E M   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestOrder(TestCase):
    """OrderItem Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(OrderItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_order_orderitem(self):
        """It should Create an order with an orderitem and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        orderitem = OrderItemFactory(order=order)
        order.orderitem.append(orderitem)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.orderitem[0].product_id, orderitem.product_id)

        orderitem2 = OrderItemFactory(order=order)
        order.orderitem.append(orderitem2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.orderitem), 2)
        self.assertEqual(new_order.orderitem[1].product_id, orderitem2.product_id)

    def test_line_amount_computed(self):
        """It should compute line_amount as price multiplied by quantity for an OrderItem"""

        order = OrderFactory()
        orderitem = OrderItemFactory(order=order, price="12.50", quantity=3)

        order.create()

        fresh = Order.find(order.id)
        self.assertEqual(len(fresh.orderitem), 1)
        self.assertEqual(str(fresh.orderitem[0].line_amount), "37.50")  # 12.50 * 3

    def test_serialize_an_orderitem(self):
        """It should Serialize an orderitem"""

        orderitem = OrderItemFactory()
        serial_orderitem = orderitem.serialize()

        self.assertEqual(serial_orderitem["id"], orderitem.id)
        self.assertEqual(serial_orderitem["order_id"], orderitem.order_id)
        self.assertEqual(serial_orderitem["product_id"], orderitem.product_id)
        self.assertEqual(serial_orderitem["price"], str(orderitem.price))
        self.assertEqual(serial_orderitem["quantity"], str(orderitem.quantity))
        self.assertEqual(serial_orderitem["line_amount"], str(orderitem.line_amount))

    def test_deserialize_an_orderitem(self):
        """It should Deserialize an orderitem"""

        orderitem = OrderItemFactory()
        orderitem.create()
        new_orderitem = OrderItem()
        new_orderitem.deserialize(orderitem.serialize())

        self.assertEqual(new_orderitem.order_id, orderitem.order_id)
        self.assertEqual(new_orderitem.product_id, orderitem.product_id)
        self.assertEqual(new_orderitem.price, orderitem.price)
        self.assertEqual(new_orderitem.quantity, orderitem.quantity)
        self.assertEqual(new_orderitem.line_amount, orderitem.line_amount)
