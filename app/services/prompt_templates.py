from langchain.prompts import ChatPromptTemplate

def get_market_analysis_template():
    return ChatPromptTemplate.from_messages([
    ('user', '''
                Given that the stock prices for the past twenty days are: {stock_prices}, and the time-series forecast for the next 7 days
                are {predicted_prices}, provide a comprehensive market analysis of the stock.
            ''')
    ])

def get_follow_up_template():
    return ChatPromptTemplate.from_messages([
        ('user', '''
                    You an assistant that responds to follow up questions based on chat history
        
                    This is the chat history with the user: {chat_history}\n
        
                    This user has a follow up question: {query}
                ''')
    ])