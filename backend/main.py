from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

app = FastAPI()

reading_df = pd.read_csv("data/reading_questions.csv")
grammar_df = pd.read_csv("data/grammar.csv")
vocab_df = pd.read_csv("data/vocab.csv")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="vector_db")
collection = client.get_collection(name="topik_knowledge_base")


class ChatRequest(BaseModel):
    question: str


class AnswerItem(BaseModel):
    question_id: int
    user_answer: str


class CheckRequest(BaseModel):
    answers: list[AnswerItem]


@app.get("/")
def home():
    return {"message": "AI_Korea Backend Running"}


def normalize_text(text: str):
    return str(text).replace(" ", "").lower()


def find_exact_grammar(query: str):
    query_norm = normalize_text(query)

    grammar_df_sorted = grammar_df.copy()
    grammar_df_sorted["keyword_length"] = grammar_df_sorted["keyword"].astype(str).str.len()
    grammar_df_sorted = grammar_df_sorted.sort_values(by="keyword_length", ascending=False)

    for _, row in grammar_df_sorted.iterrows():
        keyword_norm = normalize_text(row["keyword"])

        if keyword_norm in query_norm:
            return row

    return None


def find_exact_vocab(query: str):
    query_norm = normalize_text(query)

    vocab_df_sorted = vocab_df.copy()
    vocab_df_sorted["keyword_length"] = vocab_df_sorted["keyword"].astype(str).str.len()
    vocab_df_sorted = vocab_df_sorted.sort_values(by="keyword_length", ascending=False)

    for _, row in vocab_df_sorted.iterrows():
        keyword_norm = normalize_text(row["keyword"])

        if keyword_norm in query_norm:
            return row

    return None


def format_grammar_answer(row):
    return f"""
{row["keyword"]} — {row["title"]}

{row["explanation"]}

Examples:

1. {row["example_1"]}
   {row["translation_1"]}

2. {row["example_2"]}
   {row["translation_2"]}
""".strip()


def format_vocab_answer(row):
    return f"""
{row["keyword"]} — {row["meaning"]}

Examples:

1. {row["example_1"]}
   {row["translation_1"]}

2. {row["example_2"]}
   {row["translation_2"]}
""".strip()


def detect_query_type(query: str):
    grammar_markers = ["-", "grammar", "meaning of", "express", "tense", "particle"]

    if any(marker in query.lower() for marker in grammar_markers):
        return "grammar"

    return None


def search_knowledge_base(query: str, n_results: int = 3):
    query_embedding = model.encode([query]).tolist()
    query_type = detect_query_type(query)

    if query_type:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": query_type}
        )
    else:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

    return results["documents"][0]


def format_rag_answer(query: str, documents: list[str]):
    best_doc = documents[0]
    parts = best_doc.split(" | ")

    data = {}

    for part in parts:
        if ": " in part:
            key, value = part.split(": ", 1)
            data[key.strip()] = value.strip()

    keyword = data.get("keyword", "")
    title = data.get("title", "")
    meaning = data.get("meaning", "")
    explanation = data.get("explanation", "")
    example_1 = data.get("example_1", "")
    translation_1 = data.get("translation_1", "")
    example_2 = data.get("example_2", "")
    translation_2 = data.get("translation_2", "")

    label = title if title else meaning

    return f"""
{keyword} — {label}

{explanation}

Examples:

1. {example_1}
   {translation_1}

2. {example_2}
   {translation_2}
""".strip()


@app.post("/chat")
def chat(request: ChatRequest):
    exact_grammar = find_exact_grammar(request.question)

    if exact_grammar is not None:
        answer = format_grammar_answer(exact_grammar)
        return {"answer": answer}

    exact_vocab = find_exact_vocab(request.question)

    if exact_vocab is not None:
        answer = format_vocab_answer(exact_vocab)
        return {"answer": answer}

    docs = search_knowledge_base(request.question)
    answer = format_rag_answer(request.question, docs)

    return {"answer": answer}


@app.get("/practice/questions")
def get_questions(
    level: str = "topik_1",
    question_type: str = "grammar_fill_blank"
):
    filtered = reading_df[
        (reading_df["level"] == level) &
        (reading_df["question_type"].str.contains(question_type, case=False, na=False))
    ]

    questions = filtered.sample(min(5, len(filtered)))
    results = []

    for _, row in questions.iterrows():
        results.append({
            "number": len(results) + 1,
            "id": int(row["id"]),
            "text": row["text"],
            "question": row["question"],
            "options": {
                "1": row["option_1"],
                "2": row["option_2"],
                "3": row["option_3"],
                "4": row["option_4"]
            }
        })

    return results


@app.post("/practice/check")
def check_answers(request: CheckRequest):
    results = []

    for index, item in enumerate(request.answers, start=1):
        row = reading_df[reading_df["id"] == item.question_id]

        if row.empty:
            results.append({
                "number": index,
                "status": "not_found"
            })
            continue

        row = row.iloc[0]

        options = [
            row["option_1"],
            row["option_2"],
            row["option_3"],
            row["option_4"]
        ]

        try:
            user_answer_number = int(item.user_answer)

            if user_answer_number < 1 or user_answer_number > 4:
                raise ValueError

            user_answer_text = options[user_answer_number - 1]

        except:
            results.append({
                "number": index,
                "status": "invalid_answer",
                "message": "Answer must be a number from 1 to 4."
            })
            continue

        correct_answer = row["correct_answer"]
        is_correct = user_answer_text == correct_answer

        results.append({
            "number": index,
            "is_correct": is_correct,
            "user_answer": user_answer_text,
            "correct_answer": correct_answer,
            "explanation": row["explanation"]
        })
    return results    

@app.get("/vocab/flashcards")
def get_vocab_flashcards(
    level: str = "TOPIK I",
    count: int = 10
):
    filtered = vocab_df[vocab_df["level"] == level]

    cards = filtered.sample(min(count, len(filtered)))

    results = []

    for _, row in cards.iterrows():
        results.append({
            "id": int(row["id"]),
            "word": row["keyword"],
            "meaning": row["meaning"],
            "example": row["example_1"],
            "translation": row["translation_1"],
            "level": row["level"]
        })

    return results