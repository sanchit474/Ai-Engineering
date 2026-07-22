# from typing import TypedDict, Annotated
# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langchain_core.messages import BaseMessage
# from langgraph.checkpoint.postgres import PostgresSaver

# import os
# from psycopg import Connection

# DATABASE_URL = os.getenv("DB_CONNECTION_STRING")
# conn = Connection.connect(DATABASE_URL)

# # from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Define the state structure
# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

# # Initialize Groq model
# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0.7,
# )

# # Define the node function
# def chatbot(state: ChatState):
#     response = llm.invoke(state["messages"])
#     return {
#         "messages": [response]
#     }

# # Build the workflow graph
# builder = StateGraph(ChatState)
# builder.add_node("chatbot", chatbot)
# builder.add_edge(START, "chatbot")
# builder.add_edge("chatbot", END)


# checkpointer = PostgresSaver(conn)
# # Creates the checkpoint tables (only first run)
# checkpointer.setup()

# graph = builder.compile(checkpointer=checkpointer)

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from psycopg import Connection
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.postgres import PostgresSaver

# 1. Load environment variables before initializing connections
load_dotenv()

DATABASE_URL = os.getenv("DB_CONNECTION_STRING")
if not DATABASE_URL:
    raise ValueError("DB_CONNECTION_STRING missing from environment variables.")


# Establish connection to Neon Postgres
conn = Connection.connect(DATABASE_URL)
conn.autocommit = True

# Define the state structure
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize Groq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
)

# Define the node function
def chatbot(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": [response]
    }

# Build the workflow graph
builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Configure the persistent PostgreSQL checkpointer
checkpointer = PostgresSaver(conn)
checkpointer.setup()  # Safely creates checkpoint tables if they don't exist

# Compile the graph
graph = builder.compile(checkpointer=checkpointer)