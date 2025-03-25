from app.extensions import database, session
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import jsonpickle

class Notebook(database.Model):
    __tablename__ = 'notebooks'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    title = database.Column(database.String(255), nullable=True)
    note = database.Column(database.Text, nullable=False)
    video_info = database.Column(database.Text, nullable=False)
    created_at = database.Column(database.DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notebooks") 

    def __repr__(self):
        return f'<Notebook {self.id}>'

    
    def serialize(self):
            return {
                'id': self.id,
                "title": self.title,
                "note": self.note,
                "metadata": self.deserialize_video_info()
            }
   
    def deserialize_video_info(self):
        if not self.metadata:
            return None 
        try:
            return jsonpickle.decode(self.video_info)
        except Exception as e:
            print(f"Error decoding chat memory: {e}")
            return None