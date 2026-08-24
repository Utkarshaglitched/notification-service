from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from models import orders,notification
from db_methods.database_handler import read_all


app=FastAPI()
templates=Jinja2Templates(directory="simulation")

@app.get("/")
def orders_page(request:Request):
    
    return templates.TemplateResponse(
                request,
                "order.html"
                )


@app.get("/inbox")
def inbox(request:Request):

    return templates.TemplateResponse(
        request,
        "inbox.html"
    )


@app.post("/orders")
def handel_orders(recv:orders):
    details=notification(recv)
    queue_status=details.add_to_queue()

    if queue_status:
        print("Stored in DB success")
        return {
            "code":200,
            "message":"Your order placed!! We will notify you shortly!"
        }

    else:
        print("Storage failed!!")
        return {
            "code":400,
            "message":"unexpected Error occured!!"
        }


@app.get("/notification/{id}")
def handel_notification(id:str):

    res=read_all(id)

    return res


