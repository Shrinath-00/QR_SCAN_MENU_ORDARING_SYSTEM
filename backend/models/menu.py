from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=False)
    category = relationship("MenuCategory", back_populates="items")
