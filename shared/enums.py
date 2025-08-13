from enum import Enum

class PaymentType(str, Enum):
    online = 'online'
    manual = 'manual'

class PaymentStatus(str, Enum):
    pending = 'pending'
    paid = 'paid'
    # failed = 'failed'
    # cancelled = 'cancelled'