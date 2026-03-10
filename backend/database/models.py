from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SalesRecord(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True)
    date = Column(String(32), nullable=False)
    region = Column(String(64), nullable=False)
    product_category = Column(String(64), nullable=False)
    revenue = Column(Float, nullable=False)
    customers = Column(Integer, nullable=False)
