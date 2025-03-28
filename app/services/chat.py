
from ..constants import *
from ..repository import base
from ..models import User, Chat
from ..helpers import add_record_to_database
from flask import abort
import jsonpickle
from langchain_core.messages import HumanMessage
from .graph import get_graph

def start_chat(request):
    stock = request.get('stock')
    user_id = request.get("user_id")

    graph = get_graph()

    state = graph.invoke({'messages' : [HumanMessage(content=f"{stock}")]}, config=get_graph_configuration('1'))

    analysis = state['messages'][-1].content

    if user_id:
        chat = Chat(user_id=user_id, title=stock, graph=jsonpickle.encode(graph), memory=jsonpickle.encode([{'AI': analysis}]))
        add_record_to_database(chat)
        return {"analysis": analysis, "chat_id": chat.id, "predicted_prices": state['predicted_prices'], "stock_prices":state['stock_prices'] }

    return {"analysis": analysis}

   
def continue_chat(request):
    query = request.get('query')
    chat_id = request.get("chat_id")

    chat = base.get_record_by_field(Chat, "id", chat_id)

    serialized_chat = chat.serialize()

    graph = serialized_chat['graph']

    state = graph.invoke({'messages' : [HumanMessage(content=query)], 'follow_up': query, 'end_chat': False}, config=get_graph_configuration(1))

    response = state['messages'][-2].content

    updated_memory = serialized_chat['memory'].append([{'User': query}, {'AI': response}])

    chat.update_memory(updated_memory)
    chat.update_graph(graph)

    return{"response": response, "chat_history": updated_memory}
    

def get_graph_configuration(thread_id: int):
    return {"configurable": {"thread_id": f"{thread_id}"}}


