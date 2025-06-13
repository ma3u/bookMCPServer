
# Book MCP Server with Vector Database

## Project Overview

This project demonstrates a Python-based MCP (Model Context Protocol) server that leverages a FAISS vector database for semantic search. It's designed to ingest a text document (e.g., a book), process it into searchable chunks, and then provide an MCP endpoint to query these chunks based on semantic similarity.

This setup is a foundational example of a Retrieval Augmented Generation (RAG) component, where the MCP server acts as the retriever, fetching relevant context from the book based on a user's query.

## Table of Contents

- [Project Overview](#project-overview)
- [Preparing Your Text Data](#preparing-your-text-data)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Integrating with Claude Desktop](#integrating-with-claude-desktop)
- [Troubleshooting](#troubleshooting)

### Core Functionality

1. **Ingestion**: A script (`vector_db_ingest.py`) reads a text file, splits it into manageable chunks, generates sentence embeddings for each chunk, and stores these embeddings in a FAISS index. The corresponding text chunks are saved to a JSON file.
2. **MCP Server**: An MCP server (`mcp_server_vector.py`) loads the pre-built FAISS index and text chunks. It exposes an HTTP endpoint that accepts search queries via the Model Context Protocol.
3. **Semantic Search**: Upon receiving a query, the server generates an embedding for the query and uses the FAISS index to find the most semantically similar text chunks from the ingested book.
4. **Client**: A simple client script (`mcp_client.py`) is provided to demonstrate how to send queries to the MCP server and interpret the results.

### Technology Stack

- **Python 3**: Core programming language.
- **Sentence Transformers**: For generating high-quality semantic embeddings of text.
- **FAISS (Facebook AI Similarity Search)**: For efficient similarity search in large sets of vectors.
- **NumPy**: For numerical operations, often a dependency for FAISS and sentence-transformers.
- **Requests**: For the client to make HTTP requests to the MCP server.
- **MCP (Model Context Protocol)**: The standard used for communication between the client and the server.

## Preparing Your Text Data

If your book or document is in PDF format, you'll need to convert it to a plain text (`.txt`) file before using the `vector_db_ingest.py` script. Here are a couple of common methods:

### Using pdftotext

`pdftotext` is a utility that's part of the Poppler PDF rendering library.

**Installation:**

- **macOS (using Homebrew):**

    ```bash
    brew install poppler
    ```

- **Linux (Debian/Ubuntu):**

    ```bash
    sudo apt-get update
    sudo apt-get install poppler-utils
    ```

- **Windows:**
    Windows users can use `pdftotext` via:
  - Windows Subsystem for Linux (WSL) by installing `poppler-utils` as shown for Linux.
  - Downloading pre-compiled Poppler binaries for Windows. You may need to add the `bin` directory to your system's PATH.

**Usage:**

Once installed, run the following command in your terminal, replacing `YourBook.pdf` with your PDF file's name and `YourBook.txt` with your desired output text file name:

```bash
pdftotext YourBook.pdf YourBook.txt
```

This will create `YourBook.txt` in the same directory.

## Setup Instructions

### 1. Virtual Environment

It's highly recommended to use a virtual environment. (Note: These instructions assume you have Python 3 and `pip` installed. If not, please download Python from [python.org](https://www.python.org/) or use a package manager like Homebrew on macOS (`brew install python`)). On Windows, ensure Python is added to your PATH during installation, or use the `py` launcher (e.g., `py -m venv venv`)).

Navigate to your project directory and run:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

**Important**: Ensure you use the Python interpreter from your virtual environment (`./venv/bin/python` on macOS/Linux or `.\venv\Scripts\python` on Windows) for all subsequent commands.

### 2. Install Dependencies

Create a `requirements.txt` file in your project root with the following content:

```txt
sentence-transformers
faiss-cpu
numpy
requests
```

Then, install the packages (ensure your virtual environment is active):

```bash
# On macOS/Linux:
./venv/bin/python -m pip install -r requirements.txt
# On Windows (from project root, after activating venv):
# .\venv\Scripts\python -m pip install -r requirements.txt
```

## Usage

### 1. Data Ingestion

This step processes your book's text, creates a FAISS index, and saves the text chunks.

1. Place your book's text file (e.g., `YourBook.txt`) in the project's root directory.
2. Run the ingestion script. Replace `YourBook.txt` with your actual file name and `book_index.faiss` with your desired output index name.

```bash
# Ensure venv is active
# On macOS/Linux:
./venv/bin/python vector_db_ingest.py YourBook.txt book_index.faiss
# On Windows (from project root, after activating venv):
# .\venv\Scripts\python vector_db_ingest.py YourBook.txt book_index.faiss
```

This will produce two files (e.g., `book_index.faiss` and `book_index_chunks.json`):

- `<index_name>.faiss`: The FAISS vector index.
- `<index_name>_chunks.json`: The text chunks corresponding to the vectors.

Expected output from `vector_db_ingest.py`:

```console
Created FAISS index with <N> chunks at book_index.faiss
Saved <N> chunks to book_index_chunks.json
```

### 2. Start the MCP Server

The server loads the FAISS index and chunks, then listens for HTTP requests. Replace `book_index.faiss` if you used a different name during ingestion.

```bash
# Ensure venv is active
# On macOS/Linux:
./venv/bin/python mcp_server_vector.py book_index.faiss
# On Windows (from project root, after activating venv):
# .\venv\Scripts\python mcp_server_vector.py book_index.faiss
```

Expected server startup output (the number of chunks will vary):

```text
Loading sentence transformer model (paraphrase-multilingual-MiniLM-L12-v2)...
Loading FAISS index...
Successfully loaded 104 chunks from book_index_chunks.json
MCP Vector Server started on port 8000...
```

Keep this terminal window open. The server needs to be running to accept client requests.

### 3. Query the MCP Server

In a **new terminal window** (ensure your virtual environment is also active here), run the client script:

```bash
# On macOS/Linux:
./venv/bin/python mcp_client.py
# On Windows (from project root, after activating venv):
# .\venv\Scripts\python mcp_client.py
```

The client sends a predefined query to the server. Here's the interaction flow:

**Client Sends:**

```json
Sending query to http://localhost:8000/mcp...
Payload: {
  "name": "query",
  "input": {
    "query": "Vitamin D Mangel",
    "top_k": 5
  },
  "id": "q1"
}
```

**Server Responds (Example):**

The server will log the request (e.g., `127.0.0.1 - - [12/Jun/2025 17:33:16] "POST /mcp HTTP/1.1" 200 -`), and the client will print the JSON response:

```json
Response Status Code: 200

Response JSON:
{
  "id": "q1",
  "content": {
    "results": [
      {
        "original_id": "chunk_41",
        "text": "Vitamin D Mangel ...",
        "score": 0.06892669945955276
      },
      {
        "original_id": "chunk_36",
        "text": "Vitamin D und K2 arbeiten im Körper zusammen ... ",
        "score": 0.06125415861606598
      },
      {
        "original_id": "chunk_27",
        "text": "erhöhter Bedarf an Vitamin B6 Zielwert Vitamin B6 bioaktiv... (gekürzt für Lesbarkeit) ...",
        "score": 0.058895278722047806
      },
      {
        "original_id": "chunk_38",
        "text": "Essen, zusammen mit den anderen fettlöslichen Vitaminen oder Omega-3Fettsäuren ein, ...",
        "score": 0.057650238275527954
      },
      {
        "original_id": "chunk_32",
        "text": "Teil meiner Erfahrung, im Gegenteil. Je besser man mit Vitamin C, Calcium und Vitamin D versorgt ist, ...",
        "score": 0.056797340512275696
      }
    ],
    "query_received": "Vitamin D Mangel"
}
```

#### 3. Integrating with Claude Desktop via `claude_desktop_config.json`

To directly integrate the Book MCP Server with Claude Desktop, allowing Claude to query it like any other MCP server, you need to modify your `claude_desktop_config.json` file. This provides a much more seamless experience than manually copying and pasting.

**A. Locate Your `claude_desktop_config.json` File:**

The location of this file varies by operating system:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json` (usually `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`)
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**B. Add the Book MCP Server Configuration:**

Open `claude_desktop_config.json` in a text editor. You will see an `mcpServers` object. You need to add a new entry for your Book MCP Server within this object. If you have other servers configured, add the `"book-search"` entry alongside them.

Here is an example of what the `mcpServers` object might look like with the new entry:

```json
{
  "mcpServers": {
    "book-search": {
      "command": "/path/to/your/project/venv/bin/python",
      "args": [
        "mcp_server_vector.py",
        "book_index.faiss"
      ],
      "cwd": "/path/to/your/project/",
      "env": {}
    }
  }
}
```

## Integrating with Claude Desktop

**C. Explanation of Configuration Fields:**

- `"book-search"`: This is the key Claude Desktop will use to identify your server. You can choose a descriptive name.
- `"command"`: **Crucially, this must be the absolute path to the Python interpreter *inside your virtual environment* that you use to run the server.**
  - Example macOS/Linux: `/Users/yourname/projects/bookMCPServer/venv/bin/python`
  - Example Windows: `C:\\Users\\yourname\\projects\\bookMCPServer\\venv\\Scripts\\python.exe` (note the double backslashes in JSON)
- `"args"`: An array of arguments to pass to the `command`.
  - The first argument is usually the name of your server script (e.g., `mcp_server_vector.py`).
  - Subsequent arguments are those your server script expects (e.g., the FAISS index file name like `book_index.faiss`).
- `"cwd"`: The **absolute path to the root directory of your Book MCP Server project**. This is where `mcp_server_vector.py` and your FAISS index reside.
  - Example macOS/Linux: `/Users/yourname/projects/bookMCPServer/`
  - Example Windows: `C:\\Users\\yourname\\projects\\bookMCPServer\\`
- `"env"`: An object for any environment variables your server might need. For this project, it's typically empty.

**D. Example Configuration:**

Let's assume:

- Your project is located at `/Users/ma3u/projects/bookMCPServer/`.
- Your virtual environment is `venv` inside that project directory.
- Your server script is `mcp_server_vector.py`.
- Your FAISS index is `book_index.faiss`.

The entry in `claude_desktop_config.json` would look like this:

```json
{
  "mcpServers": {
    "local-book-rag": {
      "command": "/Users/ma3u/projects/bookMCPServer/venv/bin/python",
      "args": [
        "mcp_server_vector.py",
        "book_index.faiss"
      ],
      "cwd": "/Users/ma3u/projects/bookMCPServer/",
      "env": {}
    }
  }
}
```

**Important Notes:**

- Replace `/Users/ma3u/projects/bookMCPServer/` with the actual absolute path to *your* project directory.
- Ensure the path to the Python executable in `command` is correct for your system and virtual environment.
- If your FAISS index file has a different name, update it in the `args` array.
- After saving `claude_desktop_config.json`, you may need to restart Claude Desktop for the changes to take effect.

**E. Using in Claude Desktop:**

Once configured and Claude Desktop is restarted:

1. Ensure your `vector_db_ingest.py` script has been run to create the `.faiss` and `_chunks.json` files.
2. You no longer need to manually start `mcp_server_vector.py` in a separate terminal. Claude Desktop will start it automatically when you try to use the "local-book-rag" (or whatever you named it) server.
3. In Claude, you can now type `@local-book-rag` (or your chosen name) followed by your query, just like you would with other MCP servers.

This direct integration allows Claude to manage the server's lifecycle and makes querying your local book data much more convenient.

## Troubleshooting

### Common Errors

- **`ModuleNotFoundError`**: Ensure your virtual environment is active AND you are using the correct Python interpreter path (e.g., `./venv/bin/python`) for all scripts.
- **`Connection refused` (from client)**: Verify that `mcp_server_vector.py` is running in a separate terminal and has successfully started on the expected port (default 8000).
