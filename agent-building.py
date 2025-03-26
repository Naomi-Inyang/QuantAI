"""
Data ingestion and preprocessing
Market Analysis and Predictive Modeling
Report Generation and Visualization

"""
import os
import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, Any, List, TypedDict
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

# Fetch Stock Data Function
def fetch_stock_data(symbol, start_date, end_date):
    try:
        data = yf.download(
            symbol, 
            start=start_date, 
            end=end_date, 
            auto_adjust=True
        )
        
        data.index = pd.DatetimeIndex(data.index)
        
        return data['Close'].squeeze()
    except Exception as e:
        print(f"Data fetching error: {e}")
        return None

# Simple Moving Average Forecast Function - switch to an ML model (ARIMA)
def simple_moving_average_forecast(data, window=30, forecast_horizon=7):
    try:
        ma = data.rolling(window=window).mean()
        
        last_ma = ma.iloc[-1]
        
        forecast = np.full(forecast_horizon, last_ma)
        
        std_dev = data.std()
        confidence_interval = (
            np.array(forecast) - 1.96 * std_dev,
            np.array(forecast) + 1.96 * std_dev
        )
        
        return {
            'forecast': np.array(forecast),
            'confidence_interval': confidence_interval,
            'model_performance': {
                'standard_deviation': std_dev
            }
        }
    
    except Exception as e:
        print(f"Forecasting error: {e}")
        return None

# Generate Market Insights Function
def generate_market_insights(forecast_result, symbol):
    if forecast_result is None:
        return "Unable to generate insights due to insufficient data."
    
    forecast = forecast_result['forecast']
    ci_lower, ci_upper = forecast_result['confidence_interval']
    std_dev = forecast_result['model_performance']['standard_deviation']
    
    trend = 'stable' if std_dev < 1 else 'volatile'
    
    insights = f"""
    Market Analysis for {symbol}:
    
    Trend Prediction: {trend.capitalize()} trend expected
    
    Forecast Details:
    - Next 7-day price projection: {', '.join(map(lambda x: f'${x:.2f}', forecast))}
    - Confidence Interval: [${ci_lower.mean():.2f}, ${ci_upper.mean():.2f}]
    
    Investment Guidance:
    {'Maintain current position' if trend == 'stable' else 'Consider risk management'}
    
    Risk Assessment:
    - Volatility Indicator: {trend}
    - Standard Deviation: ${std_dev:.2f}
    - Confidence Level: 95%
    """
    
    return insights

# Agent Workflow
class FinancialAnalysisState(TypedDict):
    stock_symbol: str
    start_date: str
    end_date: str
    raw_stock_data: Any
    stock_forecast: Dict[str, Any]
    analysis_insights: str
    final_report: str

def initialize_mistral_llm(api_key=None):
    if api_key is None:
        api_key = os.getenv('MISTRAL_API_KEY')
    
    if not api_key:
        raise ValueError("Mistral API key is required.")
    
    return ChatMistralAI(
        mistral_api_key=api_key, 
        model="mistral-large-latest"
    )

def data_ingestion_node(state: FinancialAnalysisState):
    """
    Data ingestion and preprocessing node
    """
    print("Fetching stock data...")
    raw_data = fetch_stock_data(
        state['stock_symbol'], 
        state['start_date'], 
        state['end_date']
    )
    
    return {**state, 'raw_stock_data': raw_data}

def predictive_modeling_node(state: FinancialAnalysisState):

    print("Performing predictive modeling...")
    forecast_result = simple_moving_average_forecast(state['raw_stock_data'])
    
    return {**state, 'stock_forecast': forecast_result}

def generate_insights_node(state: FinancialAnalysisState):

    print("Generating market insights...")
    analysis_insights = generate_market_insights(
        state['stock_forecast'], 
        state['stock_symbol']
    )
    
    return {**state, 'analysis_insights': analysis_insights}

def llm_report_refinement_node(state: FinancialAnalysisState):

    print("Refining report with Mistral LLM...")
    
    # Initialize Mistral LLM
    llm = initialize_mistral_llm()
    
    # Prepare prompt for LLM
    report_refinement_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""
        You are a professional financial analyst assistant. 
        Enhance the following market analysis report by:
        1. Providing additional market context and macroeconomic factors
        2. Suggesting nuanced investment strategies
        3. Highlighting potential risks and opportunities
        4. Maintaining a professional and analytical tone
        5. Ensuring the insights are actionable for financial professionals
        """),
        HumanMessage(content=state['analysis_insights'])
    ])
    
    # Create chain with output parser
    chain = report_refinement_prompt | llm | StrOutputParser()
    
    # Generate refined report
    final_report = chain.invoke({})
    
    return {**state, 'final_report': final_report}

def build_financial_analysis_graph():
    
    # Build LangGraph workflow for financial analysis
    workflow = StateGraph(FinancialAnalysisState)
    
    # Add nodes
    workflow.add_node("fetch_data", data_ingestion_node)
    workflow.add_node("create_forecast", predictive_modeling_node)
    workflow.add_node("analyze_insights", generate_insights_node)
    workflow.add_node("refine_report", llm_report_refinement_node)
    
    # Define edges
    workflow.set_entry_point("fetch_data")
    workflow.add_edge("fetch_data", "create_forecast")
    workflow.add_edge("create_forecast", "analyze_insights")
    workflow.add_edge("analyze_insights", "refine_report")
    workflow.add_edge("refine_report", END)
    
    return workflow.compile()

def run_financial_analysis(symbol, start_date, end_date, mistral_api_key=None):
    # Initialize the workflow
    workflow = build_financial_analysis_graph()
    
    # Set initial state
    initial_state: FinancialAnalysisState = {
        'stock_symbol': symbol,
        'start_date': start_date,
        'end_date': end_date,
        'raw_stock_data': None,
        'stock_forecast': {},
        'analysis_insights': '',
        'final_report': ''
    }
    # Execute the workflow
    final_state = workflow.invoke(initial_state)
    
    return final_state

if __name__ == "__main__":
    result = run_financial_analysis('AAPL', '2020-01-01', '2021-01-01')
    print("\n--- Final Financial Analysis Report ---")
    print(result['final_report'])