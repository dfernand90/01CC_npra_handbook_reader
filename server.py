"""
MCP Server — NPRA Handbook Reader (HTTP transport)
Port: 8001
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from pydantic import BaseModel
from auth import setup_auth_middleware
from search_engine import search_handbooks

app = FastAPI(title="NPRA Handbook Reader MCP Server")

# Add authentication middleware
setup_auth_middleware(app)

# Add knowledge base endpoints (/resources/list, /resources/read)
from knowledge_helpers import add_knowledge_routes
add_knowledge_routes(app, server_id="npra-handbook-reader")

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

TOOLS = [
    {
        "name": "query_handbook",
        "description": "Search NPRA handbooks for regulatory clauses matching a query. Returns exact clause references with full text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question about NPRA design rules (Norwegian or English)"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5, max: 20)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]

@app.get("/mcp/tools")
async def list_tools():
    return {"tools": TOOLS}

@app.post("/mcp/tools/call")
async def call_tool(req: ToolCallRequest):
    if req.name == "query_handbook":
        try:
            query = req.arguments.get("query")
            top_k = req.arguments.get("top_k", 5)
            
            if not query:
                return {"error": "Missing required argument: query"}
                
            if top_k > 20:
                top_k = 20
                
            # Compute embedding for the query using the API
            # For the MVP, since we don't have a local model, we will call the API at query time.
            # Wait, the prompt says "no LLM call at runtime", "fully offline". 
            # Oh, if we use API embeddings, we have to call the API for the query embedding at runtime!
            # Let me load sentence-transformers here if we are completely offline, 
            # OR we call gemini api at runtime.
            # In the implementation plan I told the user Option B uses the API at ingest time. 
            # Wait, if we use the API at ingest time, we still need to compute the query embedding at query time!
            # Let me just compute the query embedding via Gemini API here.
            
            import google.generativeai as genai
            api_key = os.getenv("gemini_api")
            genai.configure(api_key=api_key)
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']
            
            # Perform vector search
            matches = search_handbooks(query_embedding, top_k=top_k)
            
            response_data = {
                "results": matches,
                "query": query,
                "total_results": len(matches)
            }
            
            return {"content": [{"type": "text", "text": json.dumps(response_data)}]}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
            
    return {"error": f"Tool not found: {req.name}"}

@app.get("/health")
async def health():
    return {"status": "ok", "server_id": "npra-handbook-reader"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
