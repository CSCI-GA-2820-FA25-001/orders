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
from service.models import db, Order, OrderItem, Status, DataValidationError

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

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  O R D E R  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order_by_customer_id(self):
        """It should Get an Order by customer_id"""
        orders = self._create_orders(3)
        resp = self.client.get(
            BASE_URL, query_string=f"customer_id={orders[1].customer_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_id"], orders[1].customer_id)

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "Customer_id does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "Status does not match"
        )

        # Todo: Uncomment this code when get_orders is implemented
        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(
            new_order["customer_id"], order.customer_id, "Customer_id does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "Status does not match"
        )
        self.assertEqual(
            new_order["created_at"],
            order.created_at.isoformat(),
            "created_at does not match",
        )
        self.assertEqual(
            new_order["updated_at"],
            order.updated_at.isoformat(),
            "updated_at does not match",
        )

    def test_get_order(self):
        """It should Read a single Order"""

        order = self._create_orders(1)[0]
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

    def test_update_order(self):
        """It should update an existing order via the API"""
        order = OrderFactory()
        resp = self.client.post(BASE_URL, json=order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        new_order["status"] = "SHIPPED"
        order_id = new_order["id"]

        # testing if the put works
        resp = self.client.put(f"{BASE_URL}/{order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated = resp.get_json()
        self.assertEqual(updated["status"], "SHIPPED")

    ######################################################################
    #  O R D E R I T E M  T E S T   C A S E S
    ######################################################################
    def test_add_orderitem(self):
        """It should Add an orderitem to an order"""
        order = self._create_orders(1)[0]
        orderitem = OrderItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/orderitems",
            json=orderitem.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], orderitem.product_id)
        self.assertEqual(data["price"], str(orderitem.price))
        self.assertEqual(data["quantity"], str(orderitem.quantity))
        self.assertEqual(data["line_amount"], str(orderitem.line_amount))

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_orderitem = resp.get_json()
        self.assertEqual(
            new_orderitem["product_id"],
            orderitem.product_id,
            "OrderItem product_id does not match",
        )

    def test_get_orderitem(self):
        """It should Get an orderitem from an order"""
        # create a known orderitem
        order = self._create_orders(1)[0]
        orderitem = OrderItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/orderitems",
            json=orderitem.serialize(),
            content_type="application/json",
        )

        # If the POST endpoint hasn't been merged yet, this will fail with 404.
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("Location", resp.headers)

        data = resp.get_json()
        logging.debug(data)

        self.assertIsNotNone(data, "Response is not JSON")
        self.assertIn("id", data, f"JSON has no 'id': {data}")

        orderitem_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/orderitems/{orderitem_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], orderitem.product_id)
        self.assertEqual(data["price"], str(orderitem.price))
        self.assertEqual(data["quantity"], str(orderitem.quantity))
        self.assertEqual(data["line_amount"], str(orderitem.line_amount))

    def test_update_orderitem(self):
        """It should Update an orderItem on an Order"""
        # create a known address
        order = self._create_orders(1)[0]
        orderItem = OrderItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/orderitems",
            json=orderItem.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        orderitem_id = data["id"]
        data["product_id"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/orderitems/{orderitem_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/orderitems/{orderitem_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], orderitem_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], "XXXX")
