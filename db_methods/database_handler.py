from db_initialise import get_session,NotificationQueue
from sqlalchemy import select
from models import orders
from datetime import datetime

def add_into(que:orders,stat):
    session=get_session()
    try:
        dat=NotificationQueue(
            order_id=que.product_id,
            product=que.product,
            notification_type=que.notification_type,
            created_at=datetime.utcnow(),
            status=stat
        )
        session.add(dat)
        session.commit()

        return True
    except:
        return False
    finally:
        session.close()


