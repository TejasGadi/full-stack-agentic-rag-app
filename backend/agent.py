from langchain import hub
from langchain.agents import create_openai_tools_agent, create_react_agent, create_tool_calling_agent
from langchain.agents import AgentExecutor

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# To store chat history for all sessions
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    global store
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# Agent with tools
def fetch_agent_with_tools(llm, tools, agenttype="react"):


    if(agenttype == "react"):
        prompt = hub.pull("hwchase17/react-chat")
        agent = create_react_agent(llm, tools, prompt)
    elif(agenttype=="tool-calling"):
        prompt = hub.pull("hwchase17/tool-calling-agent")
        agent = create_tool_calling_agent(llm, tools, prompt)
    else:
        prompt = hub.pull("hwchase17/openai-tools-agent")
        agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True, max_iterations=10)

    return agent_executor


# Agent with chat history functionality
def fetch_history_aware_agent_with_tools(llm, tools, memory):

    agent_executor = fetch_agent_with_tools(llm, tools)

    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent_with_chat_history


