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

class ChatState(TypedDict):
    # BaseMessage means any tpe of message can exit in this list like it could be human, AI,system message
    # addmessages work same as operator.add but it is more optimized with baseMessage
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b")

# ***********************************************************
@tool
def calculator(first_no: float, sec_no: float, operation: str)-> dict:
    """
    perform a basic operation on two numbers.
    Supported operations: add, sub, div, mul"""

    try:
        if operation == 'add':
            result = first_no + sec_no
        elif operation == 'sub':
            result = first_no - sec_no
        elif operation == 'div':
            if sec_no == 0:
                return {'error': 'Division by zero is not allowed'}
            result = first_no / sec_no
        elif operation == 'mul':
            result = first_no * sec_no
        else:
            return {'error': f'Unsupported operation {operation}'}

        return {'first_num': first_no, 'sec_num': sec_no, 'operation': operation, 'result': result }
    except Exception as e:
        return {'error': str(e)}
#********************************************************************************************
tools = [calculator]

llm_tools = llm.bind_tools(tools)
# ***********************************************************


def build_graph():

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

    chatbot = build_graph()

    result = await chatbot.ainvoke({'messages': [HumanMessage(content= "Find the modulus of 1232354 and 12 give answer like cricket commentor.")]})

    print(result['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())
