import chromadb
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="vector_db")
collection = client.get_collection(name="topik_knowledge_base")


def search_knowledge_base(query, n_results=3):
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    return results["documents"][0]


def format_answer(query, documents):
    answer = f"""
AI Korea Answer

Your question:
{query}

I found these relevant TOPIK materials:

"""

    for i, doc in enumerate(documents, start=1):
        answer += f"""
Result {i}
{doc}

"""

    answer += """
Summary:
Based on the retrieved TOPIK knowledge, these results are the most relevant materials for your question.

Next step:
In the final version, LLM will transform this retrieved context into a natural tutor-style explanation.
"""

    return answer


if __name__ == "__main__":
    query = input("Ask AI Korea: ")

    docs = search_knowledge_base(query)
    final_answer = format_answer(query, docs)

    print("\n" + "=" * 60)
    print(final_answer)
    print("=" * 60)