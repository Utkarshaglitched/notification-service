from pydantic import BaseModel
from db_methods.database_handler import add_into
class orders(BaseModel):
    product_id:int
    product:str
    notification_type:str


class notification:
    def __init__(self,odr:orders):
        self.order_id=odr.product_id
        self.order=odr.product
        self.notification_type=odr.notification_type

    def add_to_queue(self):
        print("Added into the QUEUE")
        return add_into(self)


