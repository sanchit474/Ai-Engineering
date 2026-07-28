-------------------------------------
          Introduction of MCP
-------------------------------------
MCP (Model Context Protocol) is an open standard that allows AI models to communicate with external tools, applications, databases, and services through a common protocol.

Think of it as:
    HTTP standardized communication between browsers and websites.

    MCP standardizes communication between AI models and tools.

Without MCP, every AI application needs custom integrations for each tool.

Example:

    ChatGPT ----> GitHub API
    ChatGPT ----> Gmail API
    ChatGPT ----> Slack API
    ChatGPT ----> PostgreSQL API

Each integration is different.
With MCP:

           ChatGPT
              |
              |
          MCP Client
              |
    ----------------------------
    |      |      |      |
    GitHub Gmail Slack Database
    MCP     MCP    MCP    MCP
    Server  Server Server Server

Every tool follows the same protocol.

-------------------------------------
          Why was MCP created? 
-------------------------------------
Before MCP:
    Suppose you build an AI assistant.
You want it to:
    Read PDFs
    Access GitHub
    Read Gmail
    Query PostgreSQL
    Search files

Without MCP:
    GitHub SDK
    Gmail SDK
    Postgres Driver
    Filesystem Library
    Slack SDK

Every SDK has:

    different authentication
    different API
    different response format
    different error handling

Your code becomes messy.

With MCP:
    One Protocol
        ↓
    Any MCP Server
        ↓
    Any Tool
The AI only needs to understand MCP.

-----------------------------------------------
Why is MCP becoming popular?

Large AI companies and tool builders are adopting it because it reduces integration work and lets tools be reused across many AI applications.

----------------------------------------------
Core Components of MCP
----------------------------------------------

There are three main components.

+-------------------------+
|         Host            |
| (Claude Desktop, IDE,   |
| AI App, etc.)           |
+-----------+-------------+
            |
            | Runs
            v
+-------------------------+
|       MCP Client        |
| Discovers & calls tools |
+-----------+-------------+
            |
            | MCP Protocol
            v
+-------------------------+
|       MCP Server        |
| Exposes tools/resources |
+-------------------------+

1. Host
The host is the application where the AI runs.

Examples:

Claude Desktop
VS Code with an AI extension
Cursor
Your own chatbot
A LangGraph application

The host doesn't directly call tools. It relies on an MCP client.

2. MCP Client
The client is responsible for:

Connecting to MCP servers
Discovering available tools
Sending tool requests
Receiving results
Passing those results back to the AI model

Think of it as the translator between the AI and external tools.

3. MCP Server

The server exposes capabilities.

For example, a filesystem server might expose:

    read_file()
    write_file()
    list_directory()
    delete_file()

A GitHub server might expose:

    create_issue()
    list_pull_requests()
    search_code()

The AI doesn't need to know how these are implemented—it just calls them through MCP.