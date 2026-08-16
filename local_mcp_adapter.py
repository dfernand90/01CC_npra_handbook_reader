from mcp.server.fastmcp import FastMCP
import requests
import json
import os

# Initialize FastMCP server
mcp = FastMCP("NPRA Handbook Reader (Remote)")

# Cloud Run API details
API_URL = "https://cc001-npra-handbook-reader-506746325258.europe-west1.run.app"
API_KEY = os.environ.get("API_KEY", "contextual0192837465")

@mcp.tool()
def query_handbook(query: str, top_k: int = 5) -> str:
    """
    Search NPRA handbooks for regulatory clauses matching a query. 
    Returns exact clause references with full text.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": "query_handbook",
        "arguments": {
            "query": query,
            "top_k": top_k
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/mcp/tools/call", 
            json=payload, 
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]
        elif "error" in data:
            return f"API Error: {data['error']}"
        return json.dumps(data, indent=2)
            
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except json.JSONDecodeError:
        return f"Failed to parse JSON response: {response.text}"

if __name__ == "__main__":
    # Start the stdio transport
    mcp.run(transport="stdio")
