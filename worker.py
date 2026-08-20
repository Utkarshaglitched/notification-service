from db_methods.database_handler import read_length,read_one,modify_status,modify_sms
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



def even_manager():
    desired_workers=1
    if read_length()>0:
        if read_length() > 100000:
            desired_workers = 1000
        elif read_length() > 10000:
            desired_workers = 100
        elif read_length() > 1000:
            desired_workers = 10
        elif read_length() > 0:
            desired_workers = 1
        else:
            desired_workers = 0

    while len(workers) < desired_workers:
        create_workers()

    while len(workers) > desired_workers:
        stop_workers()



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
