import os 

DATABASE_URL = os.getenv('DATABASE_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

#Flask Config
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')

YOUTUBE_TRANSCRIPTS_ERROR_MESSAGE = "Failed to fetch transcripts, pls try again later"

#Repsonse Messages
NOT_FOUND_MESSAGE = 'Not found'
SUCCESS_MESSAGE = 'Success'
INTERNAL_SERVER_ERROR_MESSAGE = 'Something went wrong'
INVALID_CREDENTIALS = 'Invalid Credentials'


SYSTEM_INSTRUCTION = """
"You are an assistant that can give wholesome information based on YouTube transcripts"
"Use tools only when necessary, ensure the user catches a full picture when using transcripts."
"The user does not need to specify a YouTube link, YouTube is a resource for getting the user any information they need"
"If you decide to get information from YouTube, use the tools available"
"Don't tell the user about your plans to use the tools, just use it"
"Do not hallucinate"
"""

FUNCTION_CALL_SYSTEM_INSTRUCTION = """
"You are an assistant that can perfectly the occurences from a YouTube transcript,"
" your users are able to understand a video from your description of the transcript"
"and would not need to watch the video to understand it's content"
"also provide the resources of the video incase the user chooses to check it"
"""

FUNCTION_CALL_CONFIG = {
    "tools": [
        {
            "function_declarations": [
                {
                    "name": "get_youtube_transcripts",
                    "description": "Fetches YouTube transcripts for a given topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The topic of interest for which transcripts should be retrieved.",
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
    ],

}
