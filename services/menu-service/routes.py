from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas import MenuItemResponse, MenuItemCreate, MenuItemUpdate
from controllers import get_menu_item_by_id, get_all_menu_items, create_menu_item, update_menu_item, delete_menu_item
from database import get_db
from models import MenuItem


router = APIRouter()

@router.get("/menu", response_model=List[MenuItemResponse])
def list_menu_items(db: Session = Depends(get_db)):
    return get_all_menu_items(db)

@router.get("/menu/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: UUID, db: Session = Depends(get_db)):
    item = get_menu_item_by_id(db, item_id)
    return item

@router.post("/menu", response_model=MenuItemResponse)
def create(item: MenuItemCreate, db: Session = Depends(get_db)):
    return create_menu_item(db, item)

@router.put("/menu/{item_id}", response_model=MenuItemResponse)
def update(item_id: UUID, updates: MenuItemUpdate, db: Session = Depends(get_db)):
    item = update_menu_item(db, item_id, updates)
    return item

@router.delete("/menu/{item_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: UUID, db: Session = Depends(get_db)):
    delete_menu_item(db, item_id)
    return None

