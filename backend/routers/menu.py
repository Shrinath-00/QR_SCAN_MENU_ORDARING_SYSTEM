from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.menu import MenuCategory, MenuItem
from backend.schemas.menu import MenuResponse, MenuCategorySchema, MenuItemSchema
from backend.routers.auth import RoleChecker

router = APIRouter(tags=["Menu Management"])

@router.get("/api/menu", response_model=MenuResponse)
def get_menu(db: Session = Depends(get_db)):
    categories = db.query(MenuCategory).all()
    result = []
    for cat in categories:
        result.append(MenuCategorySchema(
            id=cat.cat_id,
            name=cat.name,
            emoji="",
            description=cat.description or "",
            items=[MenuItemSchema(name=i.name, price=i.price) for i in cat.items]
        ))
    return MenuResponse(categories=result)

@router.post("/api/menu/category", status_code=status.HTTP_201_CREATED)
def add_category(cat: MenuCategorySchema, db: Session = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    existing = db.query(MenuCategory).filter(MenuCategory.cat_id == cat.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_cat = MenuCategory(
        cat_id=cat.id,
        name=cat.name,
        description=cat.description
    )
    db.add(new_cat)
    db.flush()
    for item in cat.items:
        db.add(MenuItem(
            name=item.name,
            price=item.price,
            category_id=new_cat.id
        ))
    db.commit()
    return {"message": f"Category '{cat.name}' added successfully"}

@router.put("/api/menu/item/{item_id}")
def update_item_price(item_id: int, price: float, db: Session = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.price = price
    db.commit()
    return {"message": "Price updated successfully"}

@router.delete("/api/menu/item/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user = Depends(RoleChecker(["admin"]))):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
