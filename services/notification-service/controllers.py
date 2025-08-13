from models import Notification

def create_notification(db_session, data):
    notification = Notification(**data)
    db_session.add(notification)
    db_session.commit()
    return notification

def list_notifications(db_session):
    return db_session.query(Notification).all()