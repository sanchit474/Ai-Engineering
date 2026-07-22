import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph import graph  # Import the compiled graph object securely

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
    # Fetch historical data back out from the LangGraph persistent checkpointer
    state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    
    # Format messages uniformly into dictionaries for straightforward Streamlit rendering
    formatted_messages = []
    for msg in messages:
        # LangGraph/LangChain uses "human" or "ai" (or HumanMessage/AIMessage classes)
        role = "user" if isinstance(msg, HumanMessage) or msg.type == "human" else "assistant"
        formatted_messages.append({'role': role, 'content': msg.content})
    return formatted_messages

def fetch_all_threads_from_db():
    """Queries LangGraph's checkpointer to pull all unique active thread histories."""
    threads = []
    try:
        # Pull checkpoint records out of Postgres saver
        for state in graph.checkpointer.list(config={}):
            if "configurable" in state.config and "thread_id" in state.config["configurable"]:
                t_id = state.config["configurable"]["thread_id"]
                if t_id not in threads:
                    threads.append(t_id)
    except Exception as e:
        st.sidebar.error(f"Error restoring historical threads: {e}")
    return threads

# --- Streamlit Session Initialization ---
st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖")
st.title("🤖 LangGraph Chatbot")

# 1. Fetch persistent threads from database right at startup
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = fetch_all_threads_from_db()

# 2. Handle state if no previous history was found
if not st.session_state['chat_threads']:
    initial_id = generate_thread_id()
    st.session_state['chat_threads'].append(initial_id)
    st.session_state['thread_id'] = initial_id
elif 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = st.session_state['chat_threads'][0]

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Always sync page display data with database checkpointer states on refresh
if not st.session_state['message_history'] and st.session_state['thread_id']:
    st.session_state['message_history'] = load_conversation(st.session_state['thread_id'])

# --- Sidebar Component ---
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_conversation()
    st.rerun()

st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_threads']:
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
    # 1. Update UI and Session History immediately for the new user message
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Interact with LangGraph
    with st.chat_message("assistant"):
        # Pass ONLY the newest incoming user text. 
        # LangGraph automatically resolves the historical graph data using the thread_id config.
        input_state = {"messages": [HumanMessage(content=user_input)]}
        config = {"configurable": {"thread_id": st.session_state['thread_id']}}
        
        # Generator wrapper to feed text chunks to st.write_stream securely
        def stream_generator():
            for message_chunk, metadata in graph.stream(input_state, config=config, stream_mode="messages"):
                if message_chunk.content:
                    yield message_chunk.content

        ai_response_content = st.write_stream(stream_generator())
    
    # 3. Commit the generated response text to session states
    st.session_state['message_history'].append({"role": "assistant", "content": ai_response_content})