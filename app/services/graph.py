from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from ..constants import DUMMY_STOCK_PRICES
from .prompt_templates import *

import re

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

def stock_prices(state: State):
    """fetches stock prices"""

    return DUMMY_STOCK_PRICES

def stock_forecaster(state: State):
    pattern = r"(\d{4}-\d{2}-\d{2}): \$?([\d,]+\.\d{2})"

    matches = re.findall(pattern, state['messages'][2].content)

    structured_prices = [{"date": date, "price": float(price.replace(",", ""))} for date, price in matches]

    return {'stock_prices': structured_prices, 'predicted_prices': ['1,834', '1,734', '1,934', '1,724', '1,254', '1,834', '1,734']}

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

tools = [stock_prices]
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

    graph_builder.add_edge('tools', 'stock_forecaster')
    graph_builder.add_edge('stock_forecaster', 'market_analyser')
    graph_builder.add_edge('follow_up_chatbot', 'chatbot')
    graph_builder.add_edge('market_analyser', END)
    graph_builder.set_entry_point('chatbot')

    graph = graph_builder.compile(checkpointer=memory)

    return graph
