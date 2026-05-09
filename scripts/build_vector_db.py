import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

grammar = pd.read_csv("data/grammar.csv")
vocab = pd.read_csv("data/vocab.csv")
reading = pd.read_csv("data/reading_questions.csv")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="vector_db")
collection = client.get_or_create_collection(name="topik_knowledge_base")

documents = []
ids = []
metadatas = []

def add_row(row, source):
    text = " | ".join([f"{col}: {row[col]}" for col in row.index if pd.notna(row[col])])
    doc_id = f"{source}_{row['id']}"
    
    ids.append(doc_id)
    documents.append(text)
    metadatas.append({
        "source": source,
        "type": str(row.get("type", "")),
        "level": str(row.get("level", "")),
        "keyword": str(row.get("keyword", "")) if "keyword" in row else "",
    })

for _, row in grammar.iterrows():
    add_row(row, "grammar")

for _, row in vocab.iterrows():
    add_row(row, "vocab")

for _, row in reading.iterrows():
    add_row(row, "reading")

embeddings = model.encode(documents).tolist()

collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)

print("Vector DB created successfully!")
print(f"Total documents: {len(documents)}")