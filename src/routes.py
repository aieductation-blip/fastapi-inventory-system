from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.models import InventoryItem, Base
from src.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["Items"])

class ItemCreate(BaseModel):
    name: str
    description: str = None
    quantity: int
    price: float

@router.post("/", response_model=ItemCreate)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = InventoryItem(
        name=item.name,
        description=item.description,
        quantity=item.quantity,
        price=item.price
    )
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Item creation failed")
    return db_item

@router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
