import json
import os
from dotenv import load_dotenv
from llama_stack_client.lib.agents.client_tool import client_tool
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
print(f"TAVILY_API_KEY: {TAVILY_API_KEY}")
tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Tavily client: {e}")


@client_tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily API for general information and news
    
    :param query: Search query string
    :param max_results: Maximum number of results to return (default: 5, max: 10)
    :return: JSON string with search results
    """
    if not tavily_client:
        return json.dumps({
            "error": "Tavily API key not configured. Set TAVILY_API_KEY environment variable."
        })
    
    try:
        print("************************************************")
        print("tool called: web_search")
        print(f"Searching for {query}")
        print("************************************************")
        max_results = min(max_results, 5)
        
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth="basic"
        )
        
        search_results = {
            "query": query,
            "results": []
        }
        
        for result in response.get("results", []):
            search_results["results"].append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "published_date": result.get("published_date", ""),
                "score": result.get("score", 0)
            })
        
        print("************************************************")
        print(f"Search results: {search_results}")
        print("************************************************")
        return json.dumps(search_results, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Web search failed: {str(e)}"
        })


def is_tavily_configured() -> bool:
    """Check if Tavily API key is configured"""
    return bool(TAVILY_API_KEY and tavily_client)
