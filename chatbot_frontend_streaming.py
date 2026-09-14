import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage

config = {'configurable': {'thread_id': 'thread_1'}}

# st.session_state -> dict -> is ma pehla sa pari cheza erase nhi hoti
if 'message_history' not in st.session_state:
     st.session_state['message_history']  = []

for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
         st.text(msg['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=Hello'}

user_input = st.chat_input('Type here')

if user_input:

    #first add msg to msg history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Streaming Code just make changes in 

    with st.chat_message('assistant'):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
                    {'messages': [HumanMessage(content= user_input)]},
                    config = {'configurable': {'thread_id': 'thread_1'}},
                    stream_mode = 'messages'
                 )
            )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})