# for mcp the library 
# we are using only works with asyncio so first 
# we make code asynchronous then we implement mcp
#now we remove tool an write mcp client
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
import requests
import random
from langchain_mcp_adapters.client import MultiServerMCPClient

class ChatState(TypedDict):
    # BaseMessage means any tpe of message can exit in this list like it could be human, AI,system message
    # addmessages work same as operator.add but it is more optimized with baseMessage
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b")

# ***********************************************************
#mcp client for calculator tool
client = MultiServerMCPClient(
    {
        # we can add more than 1 server
        # stdio used for server which is on local machine and we  can have another server (remote)
        'arith':{
            "transport": 'stdio',
            'command': 'python3',
            'args': ['#server path where it is saved']
        }
    }
)
#********************************************************************************************
    
# ***********************************************************


async def build_graph():

    # fetch tools from server
    tools = await client.get_tools()
    print(tools)
    llm_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState):
        """LLM node that may answer or requesta rool call"""
        # take user input
        messages = state['messages']

        # send to llm
        response = await llm_tools.ainvoke(messages)

        # return state
        return {'messages': [response]}
    # ************************************
    tool_node = ToolNode(tools)

    # ************************************
    graph = StateGraph(ChatState)

    graph.add_node('chat_node', chat_node)
    graph.add_node('tools', tool_node)

    graph.add_edge(START, 'chat_node')
    graph.add_conditional_edges('chat_node', tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()
    return chatbot

async def main():

    chatbot = await build_graph()

    result = await chatbot.ainvoke({'messages': [HumanMessage(content= "Find the modulus of 1232354 and 12 give answer like cricket commentor.")]})

    print(result['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())
