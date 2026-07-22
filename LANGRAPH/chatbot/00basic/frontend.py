# import streamlit as st

# from langchain_core.messages import HumanMessage, AIMessage

# from graph import graph

# st.set_page_config(
#     page_title="LangGraph Chatbot",
#     page_icon="🤖"
# )

# st.title("🤖 LangGraph Chatbot")

# # Store conversation
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display previous messages
# for message in st.session_state.messages:

#     if isinstance(message, HumanMessage):
#         with st.chat_message("user"):
#             st.markdown(message.content)

#     elif isinstance(message, AIMessage):
#         with st.chat_message("assistant"):
#             st.markdown(message.content)

# # Chat input
# prompt = st.chat_input("Ask anything...")

# if prompt:

#     human = HumanMessage(content=prompt)

#     st.session_state.messages.append(human)

#     with st.chat_message("user"):
#         st.markdown(prompt)

#     result = graph.invoke(
#         {
#             "messages": st.session_state.messages
#         }
#     )

#     ai = result["messages"][-1]

#     st.session_state.messages.append(ai)

#     with st.chat_message("assistant"):
#         st.markdown(ai.content)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import graph

# Page layout configuration
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖"
)

st.title("🤖 LangGraph Chatbot")

# Initialize conversation history in session state if it doesn't exist
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display conversation history on rerun
for message in st.session_state['message_history']:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Chat input from user
user_input = st.chat_input("Ask anything...")

if user_input:
    # 1. Store and render the user's message immediately
    st.session_state['message_history'].append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Render assistant bubble and stream the response
    with st.chat_message("assistant"):
        # We pass the entire history so the bot maintains context across turns
        input_state = {"messages": st.session_state['message_history']}
        config = {"configurable": {"thread_id": "thread-1"}}
        
        # st.write_stream prints chunks live and returns the full string at the end
        ai_response_content = st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in graph.stream(
                input_state,
                config=config,
                stream_mode="messages"
            )
        )
    
    # 3. Silently save the complete streamed message to history (prevents duplicates)
    st.session_state['message_history'].append(AIMessage(content=ai_response_content))