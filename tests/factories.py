"""
Test Factory to make fake objects for testing
"""

from factory import Factory, SubFactory, Sequence, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal, FuzzyNaiveDateTime
from factory import LazyAttribute
from service.models import Order, OrderItem, Status
from datetime import datetime


class OrderFactory(Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Order

    id = Sequence(lambda n: n)
    customer_id = Sequence(lambda n: f"User{n:04d}")
    status = FuzzyChoice([i for i in Status])
    created_at = FuzzyNaiveDateTime(datetime(2025, 1, 1))

    # created_at should be the same as updated_at when inserting to db
    updated_at = LazyAttribute(lambda o: o.created_at)

    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @post_generation
    def orderitem(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the orderitem list"""
        if not create:
            return

        if extracted:
            self.orderitem = extracted


class OrderItemFactory(Factory):
    """Creates fake OrderItems"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = OrderItem

    id = Sequence(lambda n: n)
    order_id = None
    product_id = Sequence(lambda n: f"SKU{n:05d}")
    price = FuzzyDecimal(0, 100, precision=2)
    quantity = FuzzyInteger(1, 100)
    order = SubFactory(OrderFactory)
