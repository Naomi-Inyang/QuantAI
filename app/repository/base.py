from ..extensions.database import session
from flask import abort
from sqlalchemy.exc import SQLAlchemyError

def get_record_by_field(model, field, value):
    data = session.query(model).filter(getattr(model, field) == value).first()
    print(data)
    if data is None:
        abort(404, f"{model.__name__} not found")

    return data

def get_records_by_field(model, field, value):
    data = session.query(model).filter(getattr(model, field) == value).order_by(getattr(model, "id").desc()).all()
    return data

def get_total_records_by_field(model, field, value):
    return session.query(model).filter(getattr(model, field) == value).count()

def update_record_field(model, field, value):
    data = session.query(model).update(getattr(model, field) == value).first()
    print(data)
    if data is None:
        abort(404, f"{model.__name__} not found")

    return data
        
    
def get_list(model):
    return session.query(model).all()

def delete_records_by_field(model, field, value):
    try:
        records = session.query(model).filter(getattr(model, field) == value)
        records.delete(synchronize_session=False)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return {"error": "Failed to delete records"}