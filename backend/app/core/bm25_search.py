"""
Elasticsearch BM25 indexing and search for Phase 4.

Chunks are indexed by document_id so they can be deleted cleanly when
a document is removed. The english analyzer applies stemming + stop-word
removal, which is what makes BM25 different from exact-match keyword search.
"""
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk
from app.config import settings

INDEX_NAME = "rag_chunks"

_client: Elasticsearch | None = None


def get_client() -> Elasticsearch:
    global _client
    if _client is None:
        _client = Elasticsearch(settings.elasticsearch_url)
    return _client


def ensure_index() -> None:
    es = get_client()
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            body={
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "chunk_id":       {"type": "keyword"},
                        "document_id":    {"type": "keyword"},
                        "document_title": {"type": "keyword"},
                        "content":        {"type": "text", "analyzer": "english"},
                        "chunk_index":    {"type": "integer"},
                        "strategy":       {"type": "keyword"},
                        "token_count":    {"type": "integer"},
                    }
                },
            },
        )


def index_chunks(chunks: list[dict]) -> int:
    """Bulk-upsert chunks into Elasticsearch. Returns number of indexed docs."""
    ensure_index()
    actions = [
        {
            "_op_type": "index",
            "_index": INDEX_NAME,
            "_id": c["chunk_id"],
            "_source": c,
        }
        for c in chunks
    ]
    success, _ = bulk(get_client(), actions)
    get_client().indices.refresh(index=INDEX_NAME)
    return success


def search(question: str, top_k: int = 5) -> list[dict]:
    """BM25 full-text search over chunk content. Returns empty list if no index."""
    es = get_client()
    try:
        resp = es.search(
            index=INDEX_NAME,
            body={
                "query": {"match": {"content": {"query": question, "operator": "or"}}},
                "size": top_k,
            },
        )
    except NotFoundError:
        return []
    return [{"score": hit["_score"], **hit["_source"]} for hit in resp["hits"]["hits"]]


def delete_document(document_id: str) -> None:
    """Remove all chunks for a document from the ES index."""
    es = get_client()
    try:
        es.delete_by_query(
            index=INDEX_NAME,
            body={"query": {"term": {"document_id": document_id}}},
        )
    except NotFoundError:
        pass
