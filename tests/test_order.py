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
Test cases for Order Model
"""

# pylint: disable=duplicate-code

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, OrderItem, DataValidationError, db
from tests.factories import OrderFactory, OrderItemFactory
from datetime import datetime, timedelta


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  O R D E R   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestOrder(TestCase):
    """Order Model Test Cases"""

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

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            customer_id=fake_order.customer_id,
            status=fake_order.status,
            created_at=fake_order.created_at,
            updated_at=fake_order.updated_at,
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, fake_order.customer_id)
        self.assertEqual(order.status, fake_order.status)
        self.assertEqual(order.created_at, fake_order.created_at)
        self.assertEqual(order.created_at, fake_order.created_at)

        # created_at should be the same as updated_at when inserting to db
        self.assertEqual(order.created_at, order.updated_at)
        self.assertEqual(order.orderitem, [])

    def test_total_amount_computed(self):
        """It should compute an Order's total_amount as the sum of all item line_amount values"""
        order = OrderFactory()

        OrderItemFactory(order=order, product_id="A", price="10.00", quantity=1)
        OrderItemFactory(order=order, product_id="B", price="2.50", quantity=3)
        OrderItemFactory(order=order, product_id="C", price="0.99", quantity=2)

        order.create()

        fresh = Order.find(order.id)
        self.assertEqual(len(fresh.orderitem), 3)
        self.assertEqual(str(fresh.total_amount), "19.48")
    
    def test_read_order(self):
        """It should Read an order"""
        fake_order = OrderFactory()
        fake_order.create()
        db.session.refresh(fake_order)

        # Read it back
        found_order = Order.find(fake_order.id)

        self.assertIsNotNone(found_order)
        self.assertEqual(found_order.id, fake_order.id)
        self.assertEqual(found_order.customer_id, fake_order.customer_id)
        self.assertEqual(found_order.status, fake_order.status)
        self.assertEqual(found_order.created_at, fake_order.created_at)
        self.assertEqual(found_order.updated_at, fake_order.updated_at)
        self.assertLessEqual(
            abs(found_order.updated_at - found_order.created_at), timedelta(seconds=1)
        )
        self.assertEqual(found_order.total_amount, 0)
        self.assertEqual(found_order.orderitem, [])

    def test_read_order_not_found(self):
        """It should return None when the order id does not exist"""
        missing_id = 99999999  # unlikely to exist
        self.assertIsNone(Order.find(missing_id))

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        orderitem = OrderItemFactory()
        order.orderitem.append(orderitem)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["customer_id"], order.customer_id)
        self.assertEqual(serial_order["status"], order.status.name)
        self.assertEqual(serial_order["total_amount"], str(order.total_amount))
        self.assertEqual(serial_order["created_at"], order.created_at.isoformat())
        self.assertEqual(serial_order["updated_at"], order.updated_at.isoformat())
        self.assertEqual(len(serial_order["orderitem"]), 1)
        orderitems = serial_order["orderitem"]
        self.assertEqual(orderitems[0]["id"], orderitem.id)
        self.assertEqual(orderitems[0]["order_id"], orderitem.order_id)
        self.assertEqual(orderitems[0]["product_id"], orderitem.product_id)
        self.assertEqual(orderitems[0]["price"], str(orderitem.price))
        self.assertEqual(orderitems[0]["quantity"], str(orderitem.quantity))
        self.assertEqual(orderitems[0]["line_amount"], str(orderitem.line_amount))

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.orderitem.append(OrderItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.status, order.status)
        self.assertEqual(new_order.created_at, order.created_at)
        self.assertEqual(new_order.updated_at, order.updated_at)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_orderitem_key_error(self):
        """It should not Deserialize an orderitem with a KeyError"""
        orderitem = OrderItem()
        self.assertRaises(DataValidationError, orderitem.deserialize, {})

    def test_deserialize_orderitem_type_error(self):
        """It should not Deserialize an orderitem with a TypeError"""
        orderitem = OrderItem()
        self.assertRaises(DataValidationError, orderitem.deserialize, [])
