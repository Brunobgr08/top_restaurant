from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException
from kafka_producer import publish_menu_updated
from models import MenuItem
from schemas import MenuItemCreate, MenuItemUpdate


def get_all_menu_items(db: Session):
    return db.query(MenuItem).all()

def get_menu_item_by_id(db: Session, item_id: UUID) -> MenuItem:

    item = db.query(MenuItem).filter_by(item_id=str(item_id)).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item do menu não encontrado")

    return item

def create_menu_item(db: Session, item_data: MenuItemCreate):
    item = MenuItem(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    publish_menu_updated(item)

    return item

def update_menu_item(db: Session, item_id: UUID, update_data: MenuItemUpdate) -> MenuItem:

    item = get_menu_item_by_id(db, item_id)

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    publish_menu_updated(item)

    return item

def delete_menu_item(db: Session, item_id: UUID):
    item = get_menu_item_by_id(db, item_id)

    db.delete(item)
    db.commit()
    return None


