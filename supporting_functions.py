from datetime import datetime
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def save_to_txt(data: str, filename: str = "market_research_notes.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"--- Market Trend Notes ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as file:
        file.write(content)

    return f"Saved successfully to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Save structured market research notes to a text file.",
)

web_search = DuckDuckGoSearchRun()


def run_market_search(query: str):
    query = query.strip()

    if not any(
        word in query.lower()
        for word in [
            "market",
            "trend",
            "industry",
            "statistics",
            "forecast",
            "segment",
            "demographic",
            "gap",
            "opportunity",
            "analysis",
        ]
    ):
        query += " market trends statistics industry report forecast analysis"

    return web_search.run(query)

search_tool = Tool(
    name="search",
    func=run_market_search,
    description="Search the web for recent market trends, supporting statistics, forecasts, industry reports, target segments, market gaps and commercial analysis",
)

wiki_search = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=150)
)

def run_wiki_search(query: str):
    return wiki_search.run(query)

wiki_tool = Tool(
    name="wikipedia",
    func=run_wiki_search,
    description="Use for background context and general reference information. Prefer web search for recent market evidence",
)