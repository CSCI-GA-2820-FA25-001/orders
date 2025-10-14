import logging
from enum import Enum
from decimal import Decimal, InvalidOperation
from .persistent_base import db, PersistentBase, DataValidationError
from .orderitem import OrderItem

"""
Models for Order

All of the models are stored in this module
"""

"""
Persistent Base class for database CRUD functions
"""


logger = logging.getLogger("flask.app")


######################################################################
#  O R D E R   M O D E L
######################################################################


class Status(Enum):
    """Enumeration of valid Order Statuses"""

    CREATED = 0
    PAID = 1
    CANCELED = 2
    SHIPPED = 3
    FULFILLED = 4
    REFUNDED = 5


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(16), nullable=False)
    status = db.Column(
        db.Enum(Status),
        nullable=False,
        default=(Status.CREATED),
        server_default=(Status.CREATED.name),
    )

    @property
    def total_amount(self):
        return sum((i.line_amount or 0) for i in self.orderitem)

    # Database auditing fields
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    orderitem = db.relationship("OrderItem", backref="order", passive_deletes=True)

    def __repr__(self):
        return (
            f"<Order id={self.id} customer_id={self.customer_id} status={self.status}>"
        )

    def serialize(self) -> dict:
        """Converts an Order into a dictionary"""

        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": self.status.name,
            "total_amount": str(self.total_amount),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "orderitem": [],
        }

        # handle inner list of orderitem
        for orderitem in self.orderitem:
            order["orderitem"].append(orderitem.serialize())

        return order

    def deserialize(self, data) -> "Order":
        """
        Populates an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.status = Status[data["status"].upper()]

            if "orderitem" in data:
                for i in list(self.orderitem):
                    db.session.delete(i)

                self.orderitem = []

            # handle inner list of orderitem
            orderitem_list = data.get("orderitem", [])
            for json_orderitem in orderitem_list:
                orderitem = OrderItem()
                orderitem.deserialize(json_orderitem)
                self.orderitem.append(orderitem)

            parsed_total = data.get("total_amount", None)
            computed_total = sum(i.line_amount for i in self.orderitem)

            if parsed_total is not None:

                if Decimal(str(parsed_total)) != computed_total:
                    logger.debug(
                        "Invalid attribute: Parsed total_amount %s not equals to computed total_amount %s",
                        parsed_total,
                        computed_total,
                    )

        except KeyError as error:
            raise DataValidationError(
                "Invalid OrderItem: missing " + error.args[0]
            ) from error

        except (InvalidOperation, ValueError, TypeError) as error:
            raise DataValidationError("Invalid numeric value in Order") from error

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Orders in the database"""
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Order by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """Returns all Orders with the given customer_id

        Args:
            customer_id (string): the id of the customer you want to match
        """
        logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()
