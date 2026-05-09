import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to DB
client = chromadb.PersistentClient(path="vector_db")
collection = client.get_collection(name="topik_knowledge_base")

# User query
query = input("Enter your question: ")

# Convert query to embedding
query_embedding = model.encode([query]).tolist()

# Search
results = collection.query(
    query_embeddings=query_embedding,
    n_results=5
)

# Print results
print("\nSEARCH RESULTS:\n")

for i, doc in enumerate(results["documents"][0]):
    print(f"RESULT {i+1}")
    print(doc)
    print("-" * 50)