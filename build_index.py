import os
import json
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

api_key = os.getenv("gemini_api")
if not api_key:
    raise ValueError("gemini_api key not found in .env")

genai.configure(api_key=api_key)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), 'knowledge')
INDEX_FILE = os.path.join(KNOWLEDGE_DIR, '_index.json')
EMBEDDINGS_FILE = os.path.join(KNOWLEDGE_DIR, '_embeddings.npy')

def embed_text(text):
    # Using text-embedding-004
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def chunk_markdown_file(filepath, handbook_id, handbook_name):
    chunks = []
    current_clause_id = ""
    current_clause_title = ""
    current_text = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("## "):
            # Save previous chunk
            if current_clause_id or current_text:
                text = "".join(current_text).strip()
                if text:
                    chunks.append({
                        "handbook_name": handbook_name,
                        "handbook_id": handbook_id,
                        "clause_id": current_clause_id,
                        "clause_title": current_clause_title,
                        "text": text
                    })
            
            # Start new chunk
            header_text = line[3:].strip()
            parts = header_text.split(" ", 1)
            if len(parts) > 1:
                current_clause_id = parts[0]
                current_clause_title = parts[1]
            else:
                current_clause_id = header_text
                current_clause_title = header_text
            current_text = []
        elif line.startswith("# "):
            pass # Main title
        else:
            current_text.append(line)
            
    # Save last chunk
    if current_clause_id or current_text:
        text = "".join(current_text).strip()
        if text:
            chunks.append({
                "handbook_name": handbook_name,
                "handbook_id": handbook_id,
                "clause_id": current_clause_id,
                "clause_title": current_clause_title,
                "text": text
            })
            
    return chunks

def build_index():
    print("Building index...")
    all_chunks = []
    
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".md") and not filename.startswith("_") and filename != "README.md" and filename != "npra_handbook_reader.md":
            filepath = os.path.join(KNOWLEDGE_DIR, filename)
            
            # We assume N400_bruprosjektering.md -> handbook_id=N400, name=N400 Bruprosjektering
            stem = os.path.splitext(filename)[0]
            parts = stem.split("_", 1)
            handbook_id = parts[0]
            handbook_name = stem.replace("_", " ").title()
            
            print(f"Processing {filename}...")
            chunks = chunk_markdown_file(filepath, handbook_id, handbook_name)
            all_chunks.extend(chunks)
            
    print(f"Total chunks: {len(all_chunks)}")
    
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        if i % 10 == 0:
            print(f"Embedding chunk {i}/{len(all_chunks)}...")
        # Create text representation for embedding
        embed_str = f"Handbook: {chunk['handbook_name']}\nClause: {chunk['clause_id']} {chunk['clause_title']}\n\n{chunk['text']}"
        vector = embed_text(embed_str)
        embeddings.append(vector)
        
    print("Saving index...")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
    np.save(EMBEDDINGS_FILE, np.array(embeddings, dtype=np.float32))
    print(f"Done. Saved to {INDEX_FILE} and {EMBEDDINGS_FILE}")

if __name__ == "__main__":
    build_index()
