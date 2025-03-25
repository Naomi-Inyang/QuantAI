from gtts import gTTS
from textblob import TextBlob

def analyze_sentiment(summary_text):
    """
    Analyzes the sentiment of the provided text and returns human-friendly interpretations.
    
    Args:
        summary_text (str): The summarized text or transcript to analyze
        
    Returns:
        dict: A dictionary containing sentiment analysis results in user-friendly format
    """
    try:
        # Perform basic sentiment analysis
        analysis = TextBlob(summary_text)
        
        # Interpret polarity (sentiment)
        if analysis.polarity > 0.5:
            sentiment = "Very positive"
        elif analysis.polarity > 0.1:
            sentiment = "Somewhat positive"
        elif analysis.polarity > -0.1:
            sentiment = "Neutral"
        elif analysis.polarity > -0.5:
            sentiment = "Somewhat negative"
        else:
            sentiment = "Very negative"
            
        # Interpret subjectivity
        if analysis.subjectivity > 0.7:
            objectivity = "Highly subjective/opinionated"
        elif analysis.subjectivity > 0.4:
            objectivity = "Somewhat subjective"
        elif analysis.subjectivity > 0.2:
            objectivity = "Fairly balanced"
        else:
            objectivity = "Highly objective/factual"
        
        # Generate a brief explanation
        explanation = f"This video appears to be {sentiment.lower()} in tone and {objectivity.lower()} in content."
        
        # # Identify key emotional words
        # emotional_words = []
        # for word, pos in analysis.tags:
        #     # Focus on adjectives, adverbs, and some verbs
        #     if pos.startswith('JJ') or pos.startswith('RB') or pos in ['VBD', 'VBG']:
        #         word_blob = TextBlob(word)
        #         if abs(word_blob.sentiment.polarity) > 0.3:
        #             emotional_words.append(word)
        
        # emotional_words = emotional_words[:5]  # Limit to top 5 emotional words
        
        # Create a user-friendly response
        result = {
            "sentiment": sentiment,
            "objectivity": objectivity,
            "explanation": explanation,
            # "emotional_words": emotional_words if emotional_words else ["No strong emotional words detected"],
            "technical": {
                "polarity": round(analysis.polarity, 2),
                "subjectivity": round(analysis.subjectivity, 2)
            }
        }
        
        return result
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return None