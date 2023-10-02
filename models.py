from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from database import Base
class Product(Base):
    __tablename__='db_product'
    product_id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), default=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=False)
    sales = relationship('Sale', back_populates='product')
    def __repr__(self):
        return f"<Task name={self.name} price={self.price}>"
        
class Sale(Base):
    __tablename__ = 'db_sale'

    sale_id = Column(Integer, primary_key=True,autoincrement=True)
    sale_date = Column(Date, nullable=False)
    product_id = Column(Integer, ForeignKey('db_product.product_id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    # Establish a relationship with the 'products' table
    product = relationship('Product', back_populates='sales')

    def __repr__(self):
        return f"<Sale sale_id={self.sale_id} sale_date={self.sale_date} product_id={self.product_id} quantity_sold={self.quantity_sold} total_price={self.total_price}>"


