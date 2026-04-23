import os, proto, json, traceback, logging
from typing import Any

import google.auth
from elasticsearch import Elasticsearch
from google.cloud import discoveryengine_v1 as discoveryengine

from google.adk.tools import ToolContext
import google.genai.types as types


def _get_gcp_project_id() -> str:
        _, adc_project_id = google.auth.default()
        if not adc_project_id:
            raise EnvironmentError(
                "GOOGLE_CLOUD_PROJECT environment variable is not set and ADC credentials do not contain a project ID."
            )
        return adc_project_id

if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = _get_gcp_project_id()
else:
     print(f"{os.getenv('GOOGLE_CLOUD_PROJECT')} is set in environment variables.")

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")

_es_client = None
_g_client = None
_ranking_config = None

def _get_es_client():
    global _es_client
    if _es_client is None:
        _es_client = Elasticsearch(
            hosts=[os.getenv("ELASTIC_API_ENDPOINT")],
            api_key=os.getenv("ELASTIC_API_KEY")
        )
    return _es_client

def _get_g_client():
    global _g_client
    if _g_client is None:
        _g_client = discoveryengine.RankServiceClient()
    return _g_client

def _get_ranking_config():
    global _ranking_config
    if _ranking_config is None:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT is not set")
        ranking_region = os.getenv("RANKING_API_REGION", "us-central1")
        _ranking_config = _get_g_client().ranking_config_path(
            project=project_id,
            location=ranking_region,
            ranking_config="default_ranking_config",
        )
    return _ranking_config

indices = ','.join([
    "search-city-code",
    "search-portal-webcontent",
    "search-portal-pdf",
    "search-city-express",
    "search-core-microsite",
    "search-adu-microsite",
    "search-scu-convention-center-microsite",
    "search-pd-press-releases",
    "search-crocker-art-museum",
    "search-sacramento-history-museum",
    "search-fairytaletown",
    "search-historicoldcitycemetery",
    "search-center-sacramento-history",
    "search-sac-zoo",
    "search-visit-sacramento",
    "search-class-specs"
])


def _build_query(query):
    TOP_K = 50
    CHUNKS_PER_DOC = 4
    return {
        "size": TOP_K,
        "_source": ["title", "url"],
        "retriever": {
            "rrf": {
                "rank_window_size": TOP_K,
                "retrievers": [
                    {
                        "standard": {
                            "query": {
                                "nested": {
                                    "path": "semantic_text.inference.chunks",
                                    "score_mode": "max",
                                    "query": {
                                        "sparse_vector": {
                                            "field": "semantic_text.inference.chunks.embeddings",
                                            "inference_id": ".elser_model_2_linux-x86_64_search",
                                            "query": query,
                                        }
                                    },
                                    "inner_hits": {"size": CHUNKS_PER_DOC, "_source": "*.text"},
                                }
                            }
                        }
                    },
                    {
                        "standard": {
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^2", "body_content"],
                                }
                            }
                        }
                    },
                ],
            }
        },
    }

def _hybrid_search(query):
    docs = []
    response = _get_es_client().search(index=indices, body=_build_query(query))
    for hit in response["hits"]["hits"]:
        if len(hit["inner_hits"]["semantic_text.inference.chunks"]["hits"]["hits"]) > 0:
            title =  hit["_source"]["title"]
            url = hit["_source"]["url"]
            for ihit in hit["inner_hits"]["semantic_text.inference.chunks"]["hits"]["hits"]:
                docs.append(
                    {
                        "doc_id": hit["_id"],
                        "index": hit["_index"],
                        "title": title,
                        "url": url,
                        "text": ihit["_source"]["text"],
                        "offset": ihit["_nested"]["offset"],
                        "score": ihit["_score"]
                    }
                )
    return docs

def _rerank(query, docs: list[dict[str,str]]):
    records = [
        discoveryengine.RankingRecord(id=  f"{doc.get("index")}/" + doc["doc_id"] + f"/{doc.get("offset")}", title=doc.get("title", ""), content=doc.get("text", ""))
        for doc in docs
    ]

    request = discoveryengine.RankRequest(
        ranking_config=_get_ranking_config(),
        query=query,
        records=records,
        top_n=10,
        model="semantic-ranker-default@latest",
        ignore_record_details_in_response=True
    )
    
    try:
        response = _get_g_client().rank(request=request)
    except Exception as e:
        logging.error(f"Something went wrong while reranking: {str(e)}", extra={"json_fields": {"query": query, "docs": docs, "records": records, "error": str(e), "traceback": traceback.format_exc()}})
        raise e
    
    ranked = [proto.Message.to_dict(r) for r in response.records]
    return ranked  # sorted by descending score

def _expand_chunks(chunk_list: list[dict[str,str]], window_k: int = 1):
    """
    Takes a list of chunk data [{"index": str, "id": str, "offset": str}, {...}, ...] and fetches each chunk from elastic along with their surrounding chunks (up to `window_k` on each side).
    """
    NESTED_PATH = "semantic_text.inference.chunks"
    searches = []
    for chunk in chunk_list:
        idx = chunk["index"]
        id = chunk["id"]
        pos = int(chunk["offset"])

        start = max(pos - window_k, 0)
        # Ask for exactly (2k+1) when possible; if pos == 0, you may only get 2
        size = 2 if pos == 0 and window_k == 1 else (2 * window_k + 1)

        header = {"index": idx}
        body = {
            # We only expect one parent hit (the doc with this _id)
            "size": 1,
            "_source": ["title", "url"],  # parent fields you want back
            "query": {
                "bool": {
                    "filter": [
                        {"ids": {"values": [id]}},
                        {
                            "nested": {
                                "path": NESTED_PATH,
                                "query": {"match_all": {}},  # match any nested doc
                                "inner_hits": {
                                    "from": start,          # <-- pick the desired position
                                    "size": size,            # exactly one inner hit at that position
                                    "_source": [f"{NESTED_PATH}.text"],
                                },
                            }
                        },
                    ]
                }
            }
        }
        searches.extend([header, body])

    results = _get_es_client().msearch(searches=searches)
    chunks_expanded = []
    for response in results.body["responses"]:
        for hit in response["hits"]["hits"]:
            chunks = []
            index = hit.get("_index", "")
            id = hit.get("_id", "")
            title = hit["_source"].get("title", "")
            url = hit["_source"].get("url", "")
            text = ""
            for ihit in hit["inner_hits"]["semantic_text.inference.chunks"]["hits"]["hits"]:
                text += ihit["_source"]["text"]
                chunks.append(ihit["_nested"]["offset"])
            chunks_expanded.append({
                "index": index,
                "id": id,
                "title": title,
                "url": url,
                "text": text,
                "chunks": chunks
            })

    return chunks_expanded

def _format_results(results: list[dict[str,str]]):
    index_map = {
        "search-city-code": "City of Sacramento Code Library",
        "search-portal-webcontent": "City of Sacramento Website",
        "search-portal-pdf": "City of Sacramento Website",
        "search-city-express": "Sacramento City Express News Publication",
        "search-core-microsite": "Cannabis Opportunity Reinvestment and Equity (CORE) Program Website",
        "search-adu-microsite": "Sacramento Accessory Dwelling Unit (ADU) Resource Center",
        "search-scu-convention-center-microsite": "SAFE Credit Union Convention Center Website",
        "search-pd-press-releases": "Sac PD Public Information Office Press Releases",
        "search-crocker-art-museum": "Crocker Art Museum Website",
        "search-sacramento-history-museum": "Sacramento History Museum Website",
        "search-fairytaletown": "Fairytale Town Website",
        "search-historicoldcitycemetery": "Sacramento Historic Old City Cemetery Website",
        "search-center-sacramento-history": "Center for Sacramento History Website",
        "search-sac-zoo": "Sacramento Zoo Website",
        "search-visit-sacramento": "Visit Sacramento Website",
        "search-class-specs": "City of Sacramento Job Class Specifications"
    }
    context = []
    for result in results:
        index_value = result.get("index", "")
        source = ""
        for key, value in index_map.items():
            if index_value.startswith(key):
                source = value
                break
        context.append({
            "source": source,
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "id": result.get("id", ""),
            "chunks": result.get("chunks", []),
            "text": result.get("text", "")
        })
    return context

# IMPORT THIS FUNCTION IN AGENT.PY AND ADD TO TOOL LIST
async def search_knowledge_tool(query: str, tool_context: ToolContext) -> list[dict[str,str]]:
    """
    This tool retrieves knowledge from the City of Sacramento.

    Args:
        question (list[str]): A single natural language query which will be used to search this data source to find answers. The query should be concise. The search tool does not support logical operators like 'OR', so don't try that. Reformulate the user's query if necessary.
        Do not include the words "Sacramento" or "City of Sacramento" in your search queries. 

    Returns:
        results (list[dict[str,str]]): List of document objects. Each document object includes a source description, title, url, and text. An empty list means no results.
    """
    try:
        docs = _hybrid_search(query)
        reranked_chunks = _rerank(query, docs)

        if not reranked_chunks:
            return []  

        chunk_list: list[dict[str,str]] = []
        for doc in reranked_chunks:
            index, id, offset = str(doc.get("id", "")).split("/", 2)
            chunk_list.append({
                "index": index,
                "id": id,
                "offset": offset
            })

        chunks_expanded: list[dict[str,str]] = _expand_chunks(chunk_list)
        context = _format_results(chunks_expanded)
    except Exception as e:
        logging.error({"message": "Error occurred during search_knowledge_tool. Continuing with empty tool result.", "query": query, "error": str(e), "traceback": traceback.format_exc()})
        return []
    return context