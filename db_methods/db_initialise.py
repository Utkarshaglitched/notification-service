import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,declarative_base,Mapped,mapped_column
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

database_url=os.getenv("DATABASE_URL")
engine=create_engine(database_url)

def get_session():
    return Session(engine)


Base=declarative_base()

class NotificationQueue(Base):
    __tablename__ = "notification_queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column()
    product: Mapped[str] = mapped_column()
    notification_type: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column()
    msg:Mapped[str]=mapped_column()

Base.metadata.create_all(engine)