from datetime import datetime, timedelta
from ..extensions.database import database
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class UserSession(database.Model):

    __tablename__ = 'user_sessions'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey("users.id"), nullable=False)
    token = database.Column(database.String(512), unique=True, nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    expires_at = database.Column(database.DateTime, nullable=False)

    def __init__(self, user_id, token, expires_in=3600):
        self.user_id = user_id
        self.token = token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
