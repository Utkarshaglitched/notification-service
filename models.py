from pydantic import BaseModel

class orders(BaseModel):
    product_id:int
    product:str
    notification_type:str


class notification:
    def __init__(self,odr:orders):
        self.order_id=odr.product_id
        self.order=odr.order
        self.notification_type=odr.notification_type

    def add_to_queue(self):
        pass


