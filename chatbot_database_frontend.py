import streamlit as st
from chatbot_database_backend import chatbot, retrieve_threads
from langchain_core.messages import HumanMessage
import uuid

# ************************* Making Utility Function (generate new thread id when this function calls) ****************************** #
def generate_thread_id():
    thread = uuid.uuid4()
    return thread

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread'] = thread_id
    add_thread(st.session_state['thread'])
    st.session_state['message_history'] = []

def add_thread(thread):
    if thread not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread)

def load_conversation(thread):
     return chatbot.get_state(config = {'configurable': {'thread_id': thread}}).values['messages']

          
# ************************************* SESSION STEUP *********************************** #
# st.session_state -> dict -> is ma pehla sa pari cheza erase nhi hoti
# saving paricular thread messages in message history
if 'message_history' not in st.session_state:
     st.session_state['message_history']  = []

# current chat thread id save in session
if 'thread' not in st.session_state:
     st.session_state['thread'] = generate_thread_id()

# Saving chat thread ids in list so we see all thread ids on sidebar
if 'chat_threads' not in st.session_state:
     # Retrieve threads tell us how many hreads are in database all those appears in sidebar
     st.session_state['chat_threads'] = retrieve_threads() 

add_thread(st.session_state['thread'])

# ************************************** SIDEBAR UI ************************************* #
st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
     reset_chat()

st.sidebar.header('Recents')

for  thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread'] = thread_id
        messages = load_conversation(thread_id)

# we did this to change the format of messages so it can load properly
        temp_msg = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else: 
                role = 'assistant' 
            temp_msg.append({'role': role, 'content':message.content})

        st.session_state['message_history'] =  temp_msg
    # we made thread_id string because button accept strings

# ************************************** MAIN UI **************************************** #
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
         st.text(msg['content'])

user_input = st.chat_input('Type here')

if user_input:

    #first add msg to msg history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Streaming Code just make changes in 
    config = {'configurable': {'thread_id': st.session_state['thread']}}

    with st.chat_message('assistant'):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
                    {'messages': [HumanMessage(content= user_input)]},
                    config = config,
                    stream_mode = 'messages'
                 )
            )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})