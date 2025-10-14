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
Order Service API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from tests.factories import OrderFactory, OrderItemFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Order, OrderItem, Status

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestOrderService(TestCase):
    """Order Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()


class TestOrderItemService(TestCase):
    """OrderItem Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        orders = []
        for _ in range(count):
            fake = OrderFactory()
            payload = {
                "customer_id": fake.customer_id,
                "status": getattr(fake.status, "name", fake.status),
                "orderitem": [],
            }
            resp = self.client.post(BASE_URL, json=payload)

            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Order"
            )
            new_id = resp.get_json()["id"]

            new_order = Order.find(new_id)
            orders.append(new_order)
        return orders

    def _create_orders_db(self, count):
        """Create orders directly via ORM (temporary helper before POST /orders is merged)."""
        orders = []
        for _ in range(count):
            fake = OrderFactory()

            order = Order(
                customer_id=fake.customer_id, status=fake.status, orderitem=[]
            )
            order.create()

            new_order = Order.find(order.id)
            orders.append(new_order)
        return orders

    ######################################################################
    #  O R D E R  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_order(self):
        """It should Read a single Order"""
        # get the id of an order
        # Todo: substitute _create_orders_db with _create_orders once POST /orders is merged
        order = self._create_orders_db(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], order.id)

    def test_get_order_not_found(self):
        """It should not Read an Order that is not found"""
        resp = self.client.get(f"{BASE_URL}/999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  O R D E R I T E M  T E S T   C A S E S
    ######################################################################
