from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class ChatState(TypedDict):
    # BaseMessage means any tpe of message can exit in this list like it could be human, AI,system message
    # addmessages work same as operator.add but it is more optimized with baseMessage
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b")
def chat_node(state: ChatState):

    # take user input
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # return state
    return {'messages': [response]}

#  first we make sqlite database then we use it

connection = sqlite3.connect(database='chatbot.db', check_same_thread=False) 
# if true code give error because sqlite work on single thread we can't used it in another thread
checkpointer = SqliteSaver(conn=connection)

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_threads():
    # used to check how many checkponts or threads we have in database
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)
