"""
Models for OrderItem

All of the models are stored in this module
"""

"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from decimal import Decimal, InvalidOperation

logger = logging.getLogger("flask.app")


######################################################################
#  O R D E R I T E M   M O D E L
######################################################################


class OrderItem(db.Model, PersistentBase):
    """
    Class that represents an OrderItem
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.String(16), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    quantity = db.Column(db.Integer, nullable=False, server_default="1")

    @property
    def line_amount(self):
        return self.price * self.quantity

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id} product_id={self.product_id}>"

    def serialize(self) -> dict:
        """Converts an OrderItem into a dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "price": str(self.price),
            "quantity": str(self.quantity),
            "line_amount": str(self.line_amount),
        }

    def deserialize(self, data: dict) -> "OrderItem":
        """
        Populates an OrderItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.order_id = data["order_id"]
            self.product_id = data["product_id"]
            self.price = Decimal(str(data["price"]))
            self.quantity = int(data["quantity"])

            parsed_line = data["line_amount"]
            computed_line = self.price * self.quantity

            if parsed_line is not None:

                if Decimal(str(parsed_line)) != computed_line:
                    logger.debug(
                        "Invalid attribute: Parsed line_amount %s not equals to computed line_amount %s",
                        parsed_line,
                        computed_line,
                    )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Address: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid OrderItem: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the OrderItems in the database"""
        logger.info("Processing all OrderItems")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a OrderItem by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_order_id(cls, order_id):
        """Returns all OrderItems with the given order_id

        Args:
            order_id (string): the id of the Order you want to match
        """
        logger.info("Processing order_id query for %s ...", order_id)
        return cls.query.filter(cls.order_id == order_id).all()
