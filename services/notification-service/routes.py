from flask import Blueprint, request, jsonify
from controllers import create_notification, list_notifications
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bp = Blueprint('notification_routes', __name__)

DATABASE_URL = 'postgresql://user:pass@notification-db:5432/notificationdb'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@bp.route('/notifications', methods=['POST'])
def add_notification():
    session = Session()
    data = request.get_json()
    notification = create_notification(session, data)
    return jsonify({'id': notification.id}), 201

@bp.route('/notifications', methods=['GET'])
def get_notifications():
    session = Session()
    notifications = list_notifications(session)
    return jsonify([{
        'id': n.id,
        'recipient': n.recipient,
        'message': n.message,
        'created_at': n.created_at.isoformat()
    } for n in notifications])