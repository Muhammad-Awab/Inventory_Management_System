from fastapi import FastAPI, status as STATUS, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from datetime import datetime, timedelta
from typing import Optional, List
from database import SessionLocal

import models
from sqlalchemy.orm import Session
app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
class Product(BaseModel):
    product_id: int
    name: str
    description: str
    price: float
    quantity: int
class SaleCreate(BaseModel):
    sale_date: date
    product_id: int
    quantity_sold: int
    total_price: float

class Sale(BaseModel):
    sale_id: int
    sale_date: date
    product_id: int
    quantity_sold: int
    total_price: float
# In-memory database to store products (for demonstration purposes)
products = []
sales = []

# API endpoint to create a new product
@app.post("/products/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())  # Create a new Product instance
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Refresh the instance to get the auto-generated ID
    return {
       
        "name": db_product.name,
        "description": db_product.description,
        "price": db_product.price,
        "quantity": db_product.quantity
    }
    
@app.get("/products/", response_model=List[Product])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()

    # Convert the list of product objects to a list of dictionaries
    product_list = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity
        }
        for product in products
    ]

    return product_list




@app.post("/sales/", response_model=SaleCreate)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    db_sale = models.Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return {
        "sale_date": db_sale.sale_date,
        "product_id": db_sale.product_id,  # Replace with the actual product ID from your products database
        "quantity_sold": db_sale.quantity_sold,
        "total_price": db_sale.total_price
    }

# API endpoint to retrieve all sales
@app.get("/sales/", response_model=List[Sale])
def get_sales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    sales = db.query(models.Sale).offset(skip).limit(limit).all()

    sales_List = [
        {
           "sale_id": sale.sale_id,
           "sale_date": sale.sale_date,
           "product_id": sale.product_id,  # Replace with the actual product ID from your products database
           "quantity_sold": sale.quantity_sold,
           "total_price": sale.total_price
        }
         for sale in sales
    ]

    return sales_List


@app.get("/products/{product_id}/sales", response_model=List[Sale])
def get_sales_for_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Query the sales associated with the specified product_id
    sales = db.query(models.Sale).filter(models.Sale.product_id == product_id).all()
    sales_List = [
        {
           "sale_id": sale.sale_id,
           "sale_date": sale.sale_date,
           "product_id": sale.product_id,  # Replace with the actual product ID from your products database
           "quantity_sold": sale.quantity_sold,
           "total_price": sale.total_price
        }
         for sale in sales
    ]

    return sales_List




@app.get("/revenue/daily")
def get_daily_revenue(db: Session = Depends(get_db)):
    # Calculate the start and end date for the current day
    today = datetime.now().date()
    start_date = today
    end_date = today + timedelta(days=1)

    # Query sales for the current day
    daily_sales = db.query(models.Sale).filter(models.Sale.sale_date >= start_date, models.Sale.sale_date < end_date).all()

    # Calculate the total revenue for the day
    total_revenue = sum(sale.total_price for sale in daily_sales)

    return {"date": today, "total_revenue": total_revenue}



@app.get("/revenue/weekly")
def get_weekly_revenue(db: Session = Depends(get_db)):
    # Calculate the start and end date for the current week
    today = datetime.now().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(weeks=1)

    # Query sales for the current week
    weekly_sales = db.query(models.Sale).filter(models.Sale.sale_date >= start_date, models.Sale.sale_date < end_date).all()

    # Calculate the total revenue for the week
    total_revenue = sum(sale.total_price for sale in weekly_sales)

    return {"start_date": start_date, "end_date": end_date, "total_revenue": total_revenue}


@app.get("/revenue/monthly")
def get_monthly_revenue(year: int, month: int, db: Session = Depends(get_db)):
    # Calculate the start and end date for the specified month and year
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()

    # Query sales for the specified month and year
    monthly_sales = db.query(models.Sale).filter(models.Sale.sale_date >= start_date, models.Sale.sale_date < end_date).all()

    # Calculate the total revenue for the specified month and year
    total_revenue = sum(sale.total_price for sale in monthly_sales)

    return {"start_date": start_date, "end_date": end_date, "total_revenue": total_revenue}


@app.get("/revenue/annual")
def get_annual_revenue(db: Session = Depends(get_db)):
    # Calculate the start and end date for the current year
    today = datetime.now().date()
    start_date = today.replace(month=1, day=1)
    end_date = today.replace(month=12, day=31)

    # Query sales for the current year
    annual_sales = db.query(models.Sale).filter(models.Sale.sale_date >= start_date, models.Sale.sale_date <= end_date).all()

    # Calculate the total revenue for the year
    total_revenue = sum(sale.total_price for sale in annual_sales)

    return {"start_date": start_date, "end_date": end_date, "total_revenue": total_revenue}
