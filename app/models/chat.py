from app.extensions import database, session
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import jsonpickle

class Chat(database.Model):
    __tablename__ = 'chats'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    title = database.Column(database.String(255), nullable=True)
    graph = database.Column(database.Text, nullable=False)
    memory = database.Column(database.Text, nullable=False)
    created_at = database.Column(database.DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chats") 

    def __repr__(self):
        return f'<Chat {self.id}>'

    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            "title": self.title,
            "memory": self.decode_data(self.memory),
            "graph": self.decode_data(self.graph)
        }
    
    def update_memory(self, memory):
        self.memory = jsonpickle.encode(memory)
        session.commit()

    def update_graph(self, graph):
        self.graph = jsonpickle.encode(graph)
        session.commit()

    def decode_data(self, data):
        if not self.metadata:
            return None 
        try:
            return jsonpickle.decode(data)
        except Exception as e:
            print(f"Error decoding chat memory: {e}")
            return None