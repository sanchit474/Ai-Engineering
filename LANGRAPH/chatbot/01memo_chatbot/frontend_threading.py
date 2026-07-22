
# import streamlit as st
# from langchain_core.messages import HumanMessage, AIMessage
# from graph import chatbot, graph
# import uuid

# # ------------utiliy function to generate unique thread IDs----------
# def generate_thread_id():
#     thread_id = uuid.uuid4()
#     return str(thread_id)

# def reset_conversation():
#     thread_id = generate_thread_id()
#     st.session_state['thread_id'] = thread_id
#     add_thread(st.session_state['thread_id'])
#     st.session_state['message_history'] = []
    

# def add_thread(thread_id):
#     if thread_id not in st.session_state['chat_threads']:
#         st.session_state['chat_threads'].append(thread_id)

# def load_conversation(thread_id):
#     # Change 'chatbot' to 'graph'
#     state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
#     return state.values.get('messages', [])

# # -----------------------------------------------------------

# # Page layout configuration
# st.set_page_config(
#     page_title="LangGraph Chatbot",
#     page_icon="🤖"
# )

# st.title("🤖 LangGraph Chatbot")

# # Initialize conversation history in session state if it doesn't exist
# # -----------session setup--------------
# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()

# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = []
# add_thread(st.session_state['thread_id'])

# # -------------------------side bar ui--------------------
# st.sidebar.title("LangGraph Chatbot")

# if st.sidebar.button('New Chat'):
#     reset_conversation()

# st.sidebar.header('My Conversations')

# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state['thread_id'] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []

#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 role='user'
#             else:
#                 role='assistant'
#             temp_messages.append({'role': role, 'content': msg.content})

#         st.session_state['message_history'] = temp_messages
    
# # st.sidebar.text(st.session_state['thread_id'])

# # -------------------------main ui-------------------------
# # Display conversation history on rerun
# for message in st.session_state['message_history']:
#     if isinstance(message, HumanMessage):
#         with st.chat_message("user"):
#             st.markdown(message.content)
#     elif isinstance(message, AIMessage):
#         with st.chat_message("assistant"):
#             st.markdown(message.content)

# # Chat input from user
# user_input = st.chat_input("Ask anything...")

# if user_input:
#     # 1. Store and render the user's message immediately
#     st.session_state['message_history'].append(HumanMessage(content=user_input))
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     # 2. Render assistant bubble and stream the response
#     with st.chat_message("assistant"):
#         # We pass the entire history so the bot maintains context across turns
#         input_state = {"messages": st.session_state['message_history']}
#         config = {"configurable": {"thread_id": st.session_state['thread_id']}}
        
#         # st.write_stream prints chunks live and returns the full string at the end
#         ai_response_content = st.write_stream(
#             message_chunk.content 
#             for message_chunk, metadata in graph.stream(
#                 input_state,
#                 config=config,
#                 stream_mode="messages"
#             )
#         )
    
#     # 3. Silently save the complete streamed message to history (prevents duplicates)
#     st.session_state['message_history'].append(AIMessage(content=ai_response_content))


# app.py
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import graph  # Import the compiled graph object

# --- Core Utility Functions ---
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_conversation():
    new_id = generate_thread_id()
    st.session_state['thread_id'] = new_id
    add_thread(new_id)
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    # Fetch data back out from the LangGraph checkpointer using the thread config
    state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    
    # Format messages uniformly into dictionaries for straightforward Streamlit rendering
    formatted_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        formatted_messages.append({'role': role, 'content': msg.content})
    return formatted_messages

# --- Streamlit Session Initialization ---
st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖")
st.title("🤖 LangGraph Chatbot")

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])

# --- Sidebar Component ---
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_conversation()

st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_threads'][::-1]:
    # Highlight which thread is currently active
    is_active = thread_id == st.session_state['thread_id']
    label = f"💬 Active: {thread_id[:8]}..." if is_active else f"📁 Thread: {thread_id[:8]}..."
    
    if st.sidebar.button(label, key=thread_id):
        st.session_state['thread_id'] = thread_id
        st.session_state['message_history'] = load_conversation(thread_id)
        st.rerun()

# --- Main UI Chat Display ---
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Interaction Workflow ---
user_input = st.chat_input("Ask anything...")

if user_input:
    # 1. Update UI and Session History immediately
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Re-instantiate LangGraph compatible state payloads from session dictionary
    with st.chat_message("assistant"):
        input_messages = [
            HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
            for m in st.session_state['message_history']
        ]
        
        input_state = {"messages": input_messages}
        config = {"configurable": {"thread_id": st.session_state['thread_id']}}
        
        # Generator wrapper to feed text chunks to st.write_stream securely
        def stream_generator():
            for message_chunk, metadata in graph.stream(input_state, config=config, stream_mode="messages"):
                if message_chunk.content:
                    yield message_chunk.content

        ai_response_content = st.write_stream(stream_generator())
    
    # 3. Commit the generated response text to session states
    st.session_state['message_history'].append({"role": "assistant", "content": ai_response_content})