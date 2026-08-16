# NPRA Handbook Reader

> Queries NPRA manuals for concrete design rules and regulatory clauses.

## Quick Facts

| Field | Value |
|---|---|
| **ID** | `npra-handbook-reader` |
| **Capability** | Composite |
| **Output Mode** | Response Creator |
| **Port** | 8001 |
| **Status** | Beta |

## What This Server Does

This server reads the Statens vegvesen (NPRA) digital manuals in PDF format and extracts concrete design rules. It combines a **knowledge base** (the bundled N400 handbook PDF and supporting documentation) with a **deterministic tool** that searches the PDF for matching regulatory clauses.

The tool takes a file path to an NPRA manual PDF and extracts sentences based on matching keywords such as "concrete", "må", "skal", and "strength". This ensures deterministic output without the overhead of an LLM for simple lookups.

Output is a JSON containing the regulatory clauses and text, which can be passed into downstream tools like the Tender Requirements Parser or QA Checklist builders.

## MCP Interface

### Tools

| Tool Name | Description | Required Inputs |
|---|---|---|
| `query_npra_rules` | Queries NPRA manuals for concrete design rules | `file_path` (string): Path to NPRA manual PDF |

### Resources

| Resource URI | Description |
|---|---|
| `knowledge://npra-handbook-reader/npra_handbook_reader` | Processing logic documentation and scope |
| `knowledge://npra-handbook-reader/N400` | NPRA N400 handbook (full PDF text extraction) |
| `knowledge://npra-handbook-reader/README` | Knowledge folder index |

## For the Customer's Agent

Call the `query_handbook` tool with a `query` (natural language question). The server will perform a vector search across indexed handbooks and return the top matching clauses as structured JSON.

You can also browse the bundled knowledge base using `/resources/list` to discover available reference documents, and `/resources/read` to read their content directly.

**Output format:**
```json
{
  "results": [
    {
      "handbook_name": "N400 Bruprosjektering",
      "handbook_id": "N400",
      "clause_id": "12.3.2",
      "clause_title": "Krav til betongoverdekning",
      "text": "For eksponeringsklasse XC3 skal...",
      "relevance_score": 0.87
    }
  ],
  "query": "concrete cover requirements XC3",
  "total_results": 1
}
```

## Setup

```bash
pip install -r requirements.txt
# Requires gemini_api key in .env for query embedding
python server.py
```

## Examples

```bash
# List tools
curl http://localhost:8001/mcp/tools

# Call tool
curl -X POST http://localhost:8001/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "query_npra_rules", "arguments": {"file_path": "/data/N400.pdf"}}'

# List knowledge resources
curl -X POST http://localhost:8001/resources/list

# Read a knowledge resource
curl -X POST http://localhost:8001/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "knowledge://npra-handbook-reader/npra_handbook_reader"}'
```
