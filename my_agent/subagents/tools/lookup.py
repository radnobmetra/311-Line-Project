import os, proto, json, traceback, logging
from typing import Any

import google.auth
from elasticsearch import Elasticsearch
from google.cloud import discoveryengine_v1 as discoveryengine

from google.adk.tools import ToolContext
import google.genai.types as types


from pathlib import Path

# Load once
DOC_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data.txt"

with open(DOC_PATH, "r", encoding="utf-8") as f:
    DOCUMENT = f.read()


def search_docs(query: str) -> str:
    """
    Very simple keyword-based search over the document.
    """

    text = DOCUMENT.lower()
    query = query.lower()

    # naive chunking
    chunks = DOCUMENT.split("\n\n")

    # score chunks by keyword overlap
    scored = []
    for chunk in chunks:
        score = sum(1 for word in query.split() if word in chunk.lower())
        if score > 0:
            scored.append((score, chunk))

    # sort by relevance
    scored.sort(reverse=True, key=lambda x: x[0])

    if not scored:
        return "No relevant information found in documents."

    # return top 2 chunks max
    top_chunks = [chunk for _, chunk in scored[:2]]

    return "\n\n".join(top_chunks)