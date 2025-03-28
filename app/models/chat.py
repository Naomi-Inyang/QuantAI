from app.extensions import database, session
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import jsonpickle
import zlib

class Chat(database.Model):
    __tablename__ = 'chats'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    title = database.Column(database.String(255), nullable=True)
    graph = database.Column(database.LargeBinary, nullable=False)
    memory = database.Column(database.LargeBinary, nullable=False)
    created_at = database.Column(database.DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chats") 

    def __repr__(self):
        return f'<Chat {self.id}>'

    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            "title": self.title,
            "memory": self.extract_data(self.memory),
            "graph": self.extract_data(self.graph)
        }
    
    def serialize_without_graph(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            "title": self.title,
            "memory": self.extract_data(self.memory)
        }
    
    def update_memory(self, memory):
        self.memory = self.compress_data(memory)
        session.commit()

    def update_graph(self, graph):
        self.graph = self.compress_data(graph)
        session.commit()

    def extract_data(self, data):
        try:
            decompressed = zlib.decompress(data).decode("utf-8")
            return jsonpickle.decode(decompressed)

        except Exception as e:
            print(f"Error decoding : {e}")
            return None
        
    def compress_data(self, data):
        string_data = jsonpickle.encode(data).encode()
        print(string_data)
        return zlib.compress(string_data)