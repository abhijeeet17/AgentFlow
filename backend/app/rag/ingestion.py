import os
import glob
import logging
from typing import List, Dict, Any
from app.rag.vectorstore import vector_store_manager

logger = logging.getLogger(__name__)

def parse_markdown_sections(file_path: str) -> List[Dict[str, Any]]:
    chunks = []
    filename = os.path.basename(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by section headers
    sections = content.split("\n## ")
    main_header = sections[0].strip().lstrip("#").strip()

    for idx, sec in enumerate(sections[1:], start=1):
        lines = sec.strip().split("\n")
        sec_title = lines[0].strip()
        sec_body = "\n".join(lines[1:]).strip()

        if sec_body:
            chunk_text = f"Document: {filename}\nTopic: {sec_title}\n{sec_body}"
            chunk_id = f"{filename}_chunk_{idx}"
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "source": filename,
                    "section": sec_title,
                    "document_type": "policy_doc"
                }
            })
            
    # If no section headers were found, store full content as a single chunk
    if not chunks and content.strip():
        chunks.append({
            "id": f"{filename}_chunk_0",
            "text": content.strip(),
            "metadata": {
                "filename": filename,
                "source": filename,
                "section": main_header or "General",
                "document_type": "policy_doc"
            }
        })
        
    return chunks

def ingest_knowledge_base(kb_directory: str) -> int:
    kb_dir = os.path.abspath(kb_directory)
    if not os.path.exists(kb_dir):
        logger.warning(f"Knowledge base directory {kb_dir} does not exist.")
        return 0

    md_files = glob.glob(os.path.join(kb_dir, "*.md"))
    total_chunks = 0
    
    docs, metadatas, ids = [], [], []

    for md_file in md_files:
        chunks = parse_markdown_sections(md_file)
        for chunk in chunks:
            docs.append(chunk["text"])
            metadatas.append(chunk["metadata"])
            ids.append(chunk["id"])
            total_chunks += 1

    if docs:
        vector_store_manager.add_documents(docs, metadatas, ids)
        logger.info(f"Ingested {total_chunks} chunks from {len(md_files)} markdown files into ChromaDB.")

    return total_chunks
