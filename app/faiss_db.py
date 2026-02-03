from langchain_community.vectorstores import FAISS
from app.embeddings import embeddings_model
from app.config import FAISS_PATH, SIMILARITY_THRESHOLD

def load_faiss_index():
    try:
        return FAISS.load_local(
            FAISS_PATH,
            embeddings_model,
            allow_dangerous_deserialization=True
        )
    except Exception:
        return None

def create_or_update_faiss(chunks_with_meta, existing_index=None):
    index = existing_index or load_faiss_index()

    texts = [c["text"] for c in chunks_with_meta]
    metas = [c["metadata"] for c in chunks_with_meta]

    if index:
        index.add_texts(texts, metadatas=metas)
    else:
        index = FAISS.from_texts(
            texts=texts,
            embedding=embeddings_model,
            metadatas=metas
        )

    index.save_local(FAISS_PATH)
    return index

def search_faiss_with_score(index, query, top_k):
    if not index:
        return []

    results = index.similarity_search_with_score(query, k=top_k)

    filtered = []
    for doc, score in results:
        if score <= SIMILARITY_THRESHOLD:
            filtered.append((doc.page_content, score, doc.metadata))

    
    if not filtered:
        filtered = [
            (doc.page_content, score, doc.metadata)
            for doc, score in results
        ]

    return filtered
    




