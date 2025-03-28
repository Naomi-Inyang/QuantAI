from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import ToolMessage
from .prompt_templates import *
from app.models import StockForecast
from app.repository import base
from langgraph.types import Command

memory = MemorySaver()

def get_llm():
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    stock_prices: list
    predicted_prices: list
    end_chat: bool
    follow_up: str
    stock: str

def stock_forecaster(state: State):
    """fetches stock prices and forecast"""

    stock_info = base.get_record_by_field(StockForecast, 'ticker', state['stock']).serialize()

    # artifact = {'stock_prices': stock_info['retrieved_data'], 'predicted_prices': stock_info['forecast']}

    return Command(update={
        'stock_prices': stock_info['retrieved_data'],
        'predicted_prices': stock_info['forecast'],
        "messages": [ToolMessage( "Successfully looked up stock forecast" )]
    })

def market_analyser(state: State):
    analyst = get_market_analysis_template() | get_llm()

    response = analyst.invoke({
        'stock_prices': state['stock_prices'], 
        'predicted_prices': state['predicted_prices']
    })

    return {'messages': [response], 'analysis': response.content}

def follow_up_chatbot(state: State):
    follow_up = get_follow_up_template() | get_llm()

    response = follow_up.invoke({
        'chat_history': state['messages'], 
        'query': state['follow_up']
    })

    return {'messages': [response], 'end_chat': True}


def route_logic(state: State):
    """Route logic to determine the next node."""
    if state.get('end_chat') == True:
        return END
    elif state.get('follow_up'):
        return 'follow_up_chatbot'
    else:
        return 'tools'

tools = [stock_forecaster]
llm_with_tools = get_llm().bind_tools(tools=tools)

def chatbot(state: State):
    response = llm_with_tools.invoke(state['messages'])
    return {'messages': [response]}


def get_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node('chatbot', chatbot)
    graph_builder.add_node('stock_forecaster', stock_forecaster)
    graph_builder.add_node('market_analyser', market_analyser)
    graph_builder.add_node('follow_up_chatbot', follow_up_chatbot)

    tool_node = ToolNode(tools=tools)

    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", route_logic, {"tools": "tools", "follow_up_chatbot": "follow_up_chatbot", END: END})

    graph_builder.add_edge('tools', 'market_analyser')
    graph_builder.add_edge('follow_up_chatbot', 'chatbot')
    graph_builder.add_edge('market_analyser', END)
    graph_builder.set_entry_point('chatbot')

    graph = graph_builder.compile(checkpointer=memory)

    return graph
