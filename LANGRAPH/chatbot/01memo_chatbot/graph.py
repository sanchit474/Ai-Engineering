from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
# from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the state structure
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize Groq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
)
# Initialize the Gemini model
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.7
# )

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

# --- THE FIX IS HERE ---
memory = MemorySaver()                               # <-- 2. Instantiate memory
graph = builder.compile(checkpointer=memory)         # <-- 3. Pass it to compile()