import serpapi
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from ..constants import *
from ..repository import base
from ..models import User, Notebook
from ..helpers import add_record_to_database
from ..util.video_metadata import VideoMetadataStore
from flask import abort
from .sentiment import analyze_sentiment
import jsonpickle
from youtube_transcript_api.proxies import WebshareProxyConfig

client = genai.Client(api_key=GEMINI_API_KEY)

def get_user_notebooks(id: int):
    notebooks = base.get_records_by_field(Notebook, "user_id", id)
    return {'notebooks' : [notebook.serialize() for notebook in notebooks]}

def get_note_from_query(user_id: int, query: str):
    base.get_record_by_field(User, 'id', user_id)

    first_response = client.models.generate_content(
        model="gemini-1.5-pro",
        config=FUNCTION_CALL_CONFIG,
        contents=f"{SYSTEM_INSTRUCTION}\n\n User Query: {query}" 
    )

    final_response = get_llm_final_response(first_response)

    metadata = VideoMetadataStore.get_metadata()

    metadata['sentiment'] = analyze_sentiment(final_response)

    notebook = Notebook(user_id=user_id, title=query, video_info=jsonpickle.encode(metadata), note=final_response)
    add_record_to_database(notebook)

    return {'query': query, "response": final_response, "metadata": metadata}


def get_llm_final_response(response):
    if hasattr(response, "text") and response.text:
        return response.text
    
    part = response.candidates[0].content.parts[0]

    available_functions = {
        "get_youtube_transcripts": get_youtube_transcripts
    }

    result = ""
    if part.function_call:
        result = call_function(part.function_call, available_functions)

    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=f"{FUNCTION_CALL_SYSTEM_INSTRUCTION}\n\n Video Transcript: {result}",
    )

    return response.text

def call_function(function_call, functions):
    function_name = function_call.name  
    function_args = function_call.args  

    func = functions.get(function_name)

    if func:
        return func(**function_args) 

    return f"Error: Function '{function_name}' not found."

def get_youtube_transcripts(query: str):
    try:
        video_data = get_related_youtube_searches(query)

        return format_transcripts(video_data)
    except:
        abort(YOUTUBE_TRANSCRIPTS_ERROR_MESSAGE), 500


def get_related_youtube_searches(query: str):
    try:
        client = serpapi.Client(api_key=SERPAPI_API_KEY)

        results = client.search({
            'search_query': query,
            'engine': 'youtube'
        })

        youtube_links = [(video['title'], video['link'], change_youtube_link_to_video_id(video['link'])) for video in results['video_results']]

        if(youtube_links): VideoMetadataStore.set_metadata(get_video_metadata(results['video_results'][0]))

        return youtube_links[:1]
    except:
        abort(YOUTUBE_TRANSCRIPTS_ERROR_MESSAGE), 500

def format_transcripts(video_data: tuple[str, str]):
    # ytt_api = YouTubeTranscriptApi()
    ytt_api = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username="mqrwokvs",
            proxy_password="z6v8pne3z7bg",
        )
    )
    youtube_transcripts = []
    for title, link, video_id in video_data:
        transcripts = ytt_api.fetch(video_id)
        transcript_text = "\n".join([transcript.text for transcript in transcripts])

        youtube_transcripts.append(f'''Title: {title}\nLink: {link}\nTranscript:\n {transcript_text}\n''')
    
    return youtube_transcripts

def change_youtube_link_to_video_id(link: str):
    return link.replace("https://www.youtube.com/watch?v=", "")

def get_video_metadata(video_data):
    return {
            "title": video_data["title"],
            "link": video_data["link"],
            "description": video_data.get("snippet", "No description available."),
            "thumbnail": video_data.get("thumbnail"),
            "views": video_data.get("views"),
            "length": video_data.get("length"),
            "published_date": video_data.get("published_date"),
        }


def get_user_total_notebooks(user_id: int):
    total_notebooks = base.get_total_records_by_field(Notebook,"user_id", user_id)
    return {'total_summaries': total_notebooks}







