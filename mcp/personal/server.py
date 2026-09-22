from fastmcp import FastMCP
import chromadb
import os
import hashlib

mcp = FastMCP("personal-mcp")

CHROMA_PATH = "/home/diego/research-jarvis/chroma/personal"
COLLECTION_NAME = "research_notes"

def get_collection():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)

def _generate_doc_id(title: str, content: str) -> str:
    """Generate deterministic document ID from title and content"""
    return "note_" + hashlib.sha256((title + content).encode()).hexdigest()[:16]

@mcp.tool()
def add_note(title: str, content: str, tags: str = "") -> str:
    """Agrega una nota personal a la base de conocimiento"""
    try:
        col = get_collection()
        doc_id = _generate_doc_id(title, content)
        col.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[{"title": title, "tags": tags}]
        )
        return f"Nota agregada: '{title}' (ID: {doc_id})"
    except Exception as e:
        return f"Error agregando nota: {str(e)}"

@mcp.tool()
def search_notes(query: str, n_results: int = 5) -> str:
    """Busca en las notas personales usando busqueda semantica"""
    try:
        col = get_collection()
        results = col.query(query_texts=[query], n_results=n_results)
        if results["ids"][0]:
            output = "Resultados:\n"
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                title = meta.get("title", "Sin titulo")
                doc = results["documents"][0][i][:200] if results["documents"] else ""
                output += f"{i+1}. [{title}] {doc}...\n"
            return output
        return "No se encontraron notas"
    except Exception as e:
        return f"Error buscando: {str(e)}"

@mcp.tool()
def list_notes() -> str:
    """Lista todas las notas personales"""
    try:
        col = get_collection()
        all_docs = col.get()
        if all_docs["ids"]:
            output = f"Total: {len(all_docs['ids'])} notas\n\n"
            for i, doc_id in enumerate(all_docs["ids"]):
                meta = all_docs["metadatas"][i] if all_docs["metadatas"] else {}
                title = meta.get("title", "Sin titulo")
                tags = meta.get("tags", "")
                output += f"{i+1}. [{title}] Tags: {tags}\n"
            return output
        return "No hay notas guardadas"
    except Exception as e:
        return f"Error listando: {str(e)}"

@mcp.tool()
def delete_note(title: str) -> str:
    """Elimina una nota por titulo"""
    try:
        col = get_collection()
        all_docs = col.get()
        for i, meta in enumerate(all_docs["metadatas"] if all_docs["metadatas"] else []):
            if meta.get("title") == title:
                col.delete(ids=[all_docs["ids"][i]])
                return f"Nota eliminada: '{title}'"
        return f"No se encontro nota con titulo: '{title}'"
    except Exception as e:
        return f"Error eliminando: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8004)
