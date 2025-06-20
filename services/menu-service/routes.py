# from flask import Blueprint, request, jsonify
# from controllers import create_menu_item, list_menu_items
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# bp = Blueprint('menu_routes', __name__)

# DATABASE_URL = 'postgresql://user:pass@menu-db:5432/menudb'
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)

# @bp.route('/menu', methods=['POST'])
# def add_menu_item():
#     session = Session()
#     data = request.get_json()
#     item = create_menu_item(session, data)
#     return jsonify({'id': item.id}), 201

# @bp.route('/menu', methods=['GET'])
# def get_menu_items():
#     session = Session()
#     items = list_menu_items(session)
#     return jsonify([{
#         'id': i.id,
#         'name': i.name,
#         'description': i.description,
#         'price': float(i.price)
#     } for i in items])






from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas import MenuItemResponse, MenuItemCreate, MenuItemUpdate
from controllers import list_menu_items, get_item_by_id, create_menu_item, update_menu_item, delete_menu_item
from database import get_db
from uuid import UUID
from typing import List
from models import MenuItem

router = APIRouter()

@router.get("/menu", response_model=List[MenuItemResponse])
def list_all(db: Session = Depends(get_db)):
    return list_menu_items(db)

@router.get("/menu/{item_id}", response_model=MenuItemResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    return get_item_by_id(db, item_id)

@router.post("/menu", response_model=MenuItemResponse)
def create(item: MenuItemCreate, db: Session = Depends(get_db)):
    return create_menu_item(db, item)

@router.put("/menu/{item_id}", response_model=MenuItemResponse)
def update(item_id: UUID, updates: MenuItemUpdate, db: Session = Depends(get_db)):
    item = update_menu_item(db, item_id, updates)
    if not item:
        raise HTTPException(404, "Item não encontrado")
    return item

@router.delete("/menu/{item_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: UUID, db: Session = Depends(get_db)):
    delete_menu_item(db, item_id)
    return None

