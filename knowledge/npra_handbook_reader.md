# NPRA Handbook Reader

## Scope
Reads the Statens vegvesen (NPRA) digital manuals in PDF format and extracts concrete design rules.

## Processing Logic
This tool takes an absolute file path to a PDF. It reads the PDF using standard Python libraries (like PyMuPDF or pypdf) and extracts sentences based on matching keywords such as "concrete", "må", "skal", and "strength". This ensures a deterministic output without the overhead of an LLM for simple lookups.

If natural language logic is strictly necessary in the future, it is configured to use the Gemini API via the .env file.

## Connection
Output is a JSON containing the regulatory clauses and text, which can seamlessly be passed into the Tender Requirements Parser or QA Checklist builders.
