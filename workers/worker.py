from db_methods.database_handler import read_one,modify_status,modify_sms
from threading import Thread,Event


workers=[]

def process(eve):

    while not eve.is_set():

        det=read_one()

        if det.get("code")==200:

            id=det.get("id")
            type=det.get("notification_type")
            product=det.get("product")
            msg=""
            sms_status=False

            if modify_status(id,"processing"):

                if type=="ORDER_PLACED":

                    msg=f"your {product} with order id: {det.get('order_id')} is placed!!"
                    sms_status=modify_sms(id,msg)

                if type=="DISPATCHED":

                    msg=f"your {product} with order id: {det.get('order_id')} is ready to distpach!!"
                    sms_status=modify_sms(id,msg)

                if type=="OUT_FOR_DELIVERY":

                    msg=f"your {product} with order id: {det.get('order_id')} is out for delivery!!"
                    sms_status=modify_sms(id,msg)

                if type=="DELIVERED":

                    msg=f"your {product} with order id: {det.get('order_id')} is delivered!!"
                    sms_status=modify_sms(id,msg)

                st=modify_status(id,"sent")

                if sms_status and st:
                    print("Notification modified in the db")


def create_workers():

    stop_event=Event()

    thread=Thread(
        target=process,
        daemon=True,
        args=(stop_event,)
    )

    thread.start()

    workers.append((thread,stop_event))


def stop_workers():

    thread,event=workers.pop()

    event.set()

    thread.join()