from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from models import orders

app=FastAPI()

templates=Jinja2Templates(directory="simulation")

@app.get("/")
def orders_page(request:Request):
    
    return templates.TemplateResponse(
                request,
                "order.html"
                )



@app.post("/orders")
def handel_orders(recv:orders):
    pass