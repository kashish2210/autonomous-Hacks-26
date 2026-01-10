# search_tool.py
from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv

load_dotenv()

search = SerpAPIWrapper(
    params={
        "engine": "google",
        "gl": "in",
        "hl": "en",
        "num": 5
    }
)
