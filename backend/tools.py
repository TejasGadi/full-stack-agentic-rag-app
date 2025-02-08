from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper, DuckDuckGoSearchAPIWrapper
# Custom RAG tool
from langchain_community.document_loaders import WebBaseLoader
from langchain.tools.retriever import create_retriever_tool

def get_agent_tools(retriever):
    # Wrappers
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=250)
    search_wrapper = DuckDuckGoSearchAPIWrapper()
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=250)

    # Tools
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)
    search_tool = DuckDuckGoSearchRun(api_wrapper=search_wrapper, name="Search Tool")
    arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)
    retrieval_tool = create_retriever_tool(name="RAG-search", description="Retrieve knowledge from the document database i.e retrieval tool RAG search",retriever=retriever)

    tools = [wiki_tool,search_tool, arxiv_tool, retrieval_tool]

    return tools

