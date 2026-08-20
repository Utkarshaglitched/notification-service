from .db_initialise import get_session,NotificationQueue
from sqlalchemy import select,func
from datetime import datetime

def add_into(que):
    session=get_session()
    try:
        dat=NotificationQueue(
            order_id=que.product_id,
            product=que.product,
            notification_type=que.notification_type,
            created_at=datetime.utcnow(),
            status="pending",
            msg=""
        )

        session.add(dat)
        session.commit()

        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()


def read_sent(id):
    session=get_session()
    try:
        cmd=select(NotificationQueue).where((NotificationQueue.order_id==id) & (NotificationQueue.status=="sent"))
        res=session.execute(cmd)
        fnd=res.scalar_one_or_none()

        if fnd is not None:

            return {
                "order_id":fnd.order_id,
                "product":fnd.product,
                "notification_type":fnd.notification_type,
                "code":200
            }
    except:

        return{
            "order_id":"",
            "product":"",
            "notification_type":"",
            "code":400
        }

    finally:
        session.close()

def read_one():
    session=get_session()
    try:
        cmd=select(NotificationQueue).where(NotificationQueue.status=="pending").limit(1)

        res=session.execute(cmd)
        fnd=res.scalar_one_or_none()

        if fnd is not None:

            return {
                "id":fnd.id,
                "order_id":fnd.order_id,
                "product":fnd.product,
                "notification_type":fnd.notification_type,
                "status":fnd.status,
                "code":200
            }
        return{
            "code":400  
        }
    except:

        return{
            "id":"",
            "order_id":"",
            "product":"",
            "notification_type":"",
            "code":400
        }

    finally:
        session.close()

def read_all(id):
    session=get_session()
    try:
        cmd=select(NotificationQueue).where((NotificationQueue.id==id)&(NotificationQueue.status=="sent")).limit(1)

        res=session.execute(cmd)
        fnd=res.scalar_one_or_none()

        if fnd is not None:

            return {
                "id":fnd.id,
                "order_id":fnd.order_id,
                "product":fnd.product,
                "msg":fnd.msg,
                "code":200
            }
        return{
            "code":400  
        }
    except:

        return{
            "id":"",
            "order_id":"",
            "product":"",
            "notification_type":"",
            "code":400
        }

    finally:
        session.close()


def read_length():
    session=get_session()
    try:
        cmd = (
            select(func.count())
            .select_from(NotificationQueue)
            .where(NotificationQueue.status == "pending")
        )

        count=session.scalar(cmd)

        return int(count)
            


    except:
        return -1



def modify_status(id,set_status):
    session=get_session()
    try:
        cmd=select(NotificationQueue).where(NotificationQueue.id==id)
        res=session.scalar(cmd)

        if res:
            res.status=set_status
            session.commit()

            return True

    except:
        return False

    finally:
        session.close()



def modify_sms(id,sms):
    session=get_session()

    try:
            cmd=select(NotificationQueue).where(NotificationQueue.id==id)
            res=session.scalar(cmd)
    
            if res:
                res.msg=sms
                session.commit()
    
                return True
    
    except:
        return False

    finally:
        session.close()


