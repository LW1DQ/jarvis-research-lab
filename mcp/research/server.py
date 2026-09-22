from fastmcp import FastMCP
import httpx
import asyncio
import json
import xml.etree.ElementTree as ET
import time
from typing import Optional

mcp = FastMCP("research-mcp")

# Async HTTP client with connection pooling
_http_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    return _http_client

async def close_http_client():
    global _http_client
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None

async def _retry_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    params: dict = None,
    timeout: float = 60.0,
    max_retries: int = 3
) -> httpx.Response:
    """Retry HTTP request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            resp = await client.request(method, url, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = min(2 ** attempt * 5, 60)
                await asyncio.sleep(wait)
                continue
            if resp.status_code < 500:
                return resp
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
            continue
    raise httpx.HTTPStatusError(f"Max retries ({max_retries}) exceeded", request=None, response=None)

@mcp.tool()
def search_papers(query: str, max_results: int = 10) -> str:
    """Busca papers en la base de conocimiento local"""
    return f"Buscando: {query} (max {max_results})"

@mcp.tool()
def summarize_paper(paper_path: str) -> str:
    """Resume un paper dado su path"""
    return f"Resumen de {paper_path}"

@mcp.tool()
def find_gaps(topic: str) -> str:
    """Encuentra gaps de investigacion en un tema"""
    return f"Gaps en {topic}: pendiente implementar"

@mcp.tool()
async def search_openalex(query: str, max_results: int = 5, timeout: int = 30) -> str:
    """Busca papers en OpenAlex con reintentos (async)"""
    client = await get_http_client()
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": max_results,
        "filter": "type:article"
    }
    
    try:
        resp = await _retry_request(client, "GET", url, params=params, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for work in data.get("results", []):
                title = work.get("title", "N/A")
                authors = ", ".join([a["author"]["name"] for a in work.get("authorships", [])[:3]])
                abstract = work.get("abstract", "")[:200] if work.get("abstract") else ""
                results.append(f"- {title} by {authors}\n  Abstract: {abstract}")
            return f"OpenAlex results for '{query}':\n" + "\n".join(results) if results else "No results found"
        elif resp.status_code == 429:
            return "Error OpenAlex: Rate limited"
        else:
            return f"Error OpenAlex: HTTP {resp.status_code}"
    except Exception as e:
        return f"Error OpenAlex: {str(e)}"

@mcp.tool()
async def search_crossref(query: str, max_results: int = 5, timeout: int = 30) -> str:
    """Busca metadata en Crossref con reintentos (async)"""
    client = await get_http_client()
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": max_results
    }
    
    try:
        resp = await _retry_request(client, "GET", url, params=params, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            message = data.get("message", {})
            results = []
            for item in message.get("items", [])[:max_results]:
                title = item.get("title", ["N/A"])[0] if item.get("title") else "N/A"
                authors = ", ".join([a["name"] for a in item.get("author", [])[:3]]) if item.get("author") else "N/A"
                doi = item.get("DOI", "N/A")
                results.append(f"- {title}\n  Authors: {authors}\n  DOI: {doi}")
            return f"Crossref results for '{query}':\n" + "\n".join(results) if results else "No results found"
        elif resp.status_code == 429:
            return "Error Crossref: Rate limited"
        else:
            return f"Error Crossref: HTTP {resp.status_code}"
    except Exception as e:
        return f"Error Crossref: {str(e)}"

@mcp.tool()
async def search_arxiv(query: str, max_results: int = 5, timeout: int = 60) -> str:
    """Busca preprints en arXiv con reintentos y timeout configurable (async)"""
    client = await get_http_client()
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "max_results": max_results
    }
    
    try:
        resp = await _retry_request(client, "GET", url, params=params, timeout=timeout)
        if resp.status_code == 200:
            root = ET.fromstring(resp.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            results = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else "N/A"
                authors = ", ".join([a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)[:3]]) if entry.findall('atom:author', ns) else "N/A"
                abstract = entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else ""
                results.append(f"- {title}\n  Authors: {authors}\n  Abstract: {abstract[:200]}")
            return f"arXiv results for '{query}':\n" + "\n".join(results) if results else "No results found"
        elif resp.status_code == 429:
            return "Error arXiv: Rate limited"
        else:
            return f"Error arXiv: HTTP {resp.status_code}"
    except Exception as e:
        return f"Error arXiv: {str(e)}"

@mcp.tool()
def search_knowledge(query: str, max_results: int = 5) -> str:
    """Busca en conocimiento indexado (ChromaDB + LDR)"""
    return f"Búsqueda de conocimiento para: {query} (max {max_results}) - Pendiente de integración con LDR"

@mcp.tool()
def save_research_note(title: str, content: str, category: str = "general") -> str:
    """Guarda una nota de investigación"""
    import os
    notes_dir = "/home/diego/research-jarvis/projects"
    os.makedirs(notes_dir, exist_ok=True)
    note_path = os.path.join(notes_dir, f"{title.replace(' ', '_')}.md")
    with open(note_path, "w") as f:
        f.write(content)
    return f"Nota guardada en: {note_path}"

if __name__ == "__main__":
    import asyncio
    
    async def run_server():
        try:
            await mcp.run_async(transport="http", host="127.0.0.1", port=8001)
        finally:
            await close_http_client()
    
    asyncio.run(run_server())
