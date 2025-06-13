# mcp_server_vector.py
import json
import sys
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from http.server import HTTPServer, BaseHTTPRequestHandler

@dataclass
class MCPRequest:
    name: str
    input: Dict[str, Any]
    id: str

@dataclass
class MCPResponse:
    id: str
    content: Dict[str, Any]
    error: Optional[str] = None

class VectorDB:
    def __init__(self, model: SentenceTransformer, index: faiss.Index, chunks_with_ids: List[Dict[str, Any]]):
        self.model = model
        self.index = index
        self.chunks_with_ids = chunks_with_ids
        # Create a mapping from original_id to chunk text for quick lookup
        self.id_to_chunk_text = {item['original_id']: item['text'] for item in self.chunks_with_ids}

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx >= 0 and idx < len(self.chunks_with_ids):
                # The 'idx' from FAISS is the position in the array used for self.index.add()
                # This should correspond to the order in self.chunks_with_ids if ingested sequentially.
                original_id = self.chunks_with_ids[idx].get('original_id', f"unknown_id_{idx}")
                text_content = self.id_to_chunk_text.get(original_id, "Content not found")
                results.append({
                    "original_id": original_id,
                    "text": text_content,
                    "score": float(1.0 / (1.0 + distance)) # Example score, can be adjusted
                })
            else:
                # Handle cases where idx might be out of bounds or -1 (no result)
                print(f"Warning: FAISS index {idx} out of bounds or invalid.")
        return results

class MCPServer:
    def __init__(self, model: SentenceTransformer, index: faiss.Index, chunks_with_ids: List[Dict[str, Any]], handler_class, port: int):
        self.vdb = VectorDB(model, index, chunks_with_ids)
        self.handlers = {"query": self.handle_query}
        self.handler_class = handler_class
        self.port = port
    
    def handle_query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 3)
        # The search method now returns richer results including text
        return {"results": self.vdb.search(query, top_k), "query_received": query}
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request = MCPRequest(**message)
            handler = self.handlers.get(request.name)
            if not handler:
                return asdict(MCPResponse(id=request.id, error=f"Invalid handler: {request.name}"))
            
            result = handler(request.input)
            return asdict(MCPResponse(id=request.id, content=result))
        
        except Exception as e:
            return asdict(MCPResponse(id=message.get("id", ""), error=f"Error: {str(e)}"))

    def run(self):
        server_address = ('', self.port)
        httpd = HTTPServer(server_address, self.handler_class)
        print(f"MCP Vector Server started on port {self.port}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("MCP Vector Server stopped.")
        finally:
            httpd.server_close()
            print("Cleaning up...")

class CustomRequestHandler(BaseHTTPRequestHandler):
    # This class will be assigned the mcp_server_instance at runtime
    mcp_server_instance: 'MCPServer' 

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            message = json.loads(body.decode('utf-8')) # Ensure decoding
            
            # Access the process_message method from the mcp_server_instance
            response_data = self.mcp_server_instance.process_message(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"id": message.get("id") if isinstance(message, dict) else "unknown", "error": f"Bad Request: Invalid JSON - {e}"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"id": message.get("id") if isinstance(message, dict) else "unknown", "error": f"Internal Server Error: {e}"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mcp_server_vector.py <faiss_index_path> [port]")
        sys.exit(1)

    FAISS_INDEX_PATH = sys.argv[1]
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

    print("Loading sentence transformer model (paraphrase-multilingual-MiniLM-L12-v2)...")
    # Load model once
    sbert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') 
    print("Loading FAISS index...")
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    # Load chunks_with_ids from the JSON file created during ingestion
    chunks_json_path = FAISS_INDEX_PATH.replace('.faiss', '_chunks.json')
    try:
        with open(chunks_json_path, 'r', encoding='utf-8') as f:
            chunks_with_ids = json.load(f)
        print(f"Successfully loaded {len(chunks_with_ids)} chunks from {chunks_json_path}")
    except FileNotFoundError:
        print(f"Error: Chunks JSON file not found at {chunks_json_path}. Ensure it was created by vector_db_ingest.py.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {chunks_json_path}: {e}")
        sys.exit(1)

    # Create the MCPServer instance, passing the loaded model, index, chunks, handler, and port
    mcp_server = MCPServer(sbert_model, faiss_index, chunks_with_ids, CustomRequestHandler, PORT)
    
    # Assign the MCPServer instance to the handler class so it can be accessed in do_POST
    CustomRequestHandler.mcp_server_instance = mcp_server
    
    mcp_server.run()
