"""
Common Status Enum for Order Service
"""

from enum import Enum


class Status(Enum):
    """Enumeration of valid Order Statuses"""
    CREATED = 0
    PAID = 1
    CANCELED = 2
    SHIPPED = 3
    FULFILLED = 4
    REFUNDED = 5
