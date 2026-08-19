from db_initialise import get_session,NotificationQueue
from sqlalchemy import select
from datetime import datetime

def add_into(que):
    session=get_session()
    try:
        dat=NotificationQueue(
            order_id=que.product_id,
            product=que.product,
            notification_type=que.notification_type,
            created_at=datetime.utcnow(),
            status="pending"
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
        cmd=select(NotificationQueue).where(NotificationQueue.order_id==id and NotificationQueue.status=="sent")
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