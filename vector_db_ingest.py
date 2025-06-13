# vector_db_ingest.py
import sys
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json

def create_vector_db(book_path: str, output_index: str, chunk_size: int = 1000, overlap: int = 200):
    # Load and chunk text
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    words = text.split()
    chunks = [' '.join(words[i:i+chunk_size]) 
             for i in range(0, len(words), chunk_size - overlap)]
    
    # Create embeddings
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(chunks)
    
    # Create and save FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    faiss.write_index(index, output_index)
    print(f"Created FAISS index with {len(chunks)} chunks at {output_index}")

    # Prepare chunks with original IDs for saving
    chunks_with_ids = [
        {"original_id": f"chunk_{i}", "text": chunk_text} 
        for i, chunk_text in enumerate(chunks)
    ]

    # Save chunks to a JSON file
    chunks_json_path = output_index.replace('.faiss', '_chunks.json')
    with open(chunks_json_path, 'w', encoding='utf-8') as f_json:
        json.dump(chunks_with_ids, f_json, ensure_ascii=False, indent=4)
    print(f"Saved {len(chunks_with_ids)} chunks to {chunks_json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vector_db_ingest.py <book.txt> <output_index.faiss>", file=sys.stderr)
        sys.exit(1)
    
    create_vector_db(sys.argv[1], sys.argv[2])
