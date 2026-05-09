# 🇰🇷 AI_Korea

AI_Korea is an AI-powered assistant for learning Korean and preparing for the TOPIK exam.

The project combines:
- Korean grammar explanations
- Vocabulary learning
- TOPIK reading practice
- Semantic search
- RAG (Retrieval-Augmented Generation)
- Vector Database technology
- LLM-based responses

---

# 📌 Project Goal

The goal of AI_Korea is to help users study Korean more efficiently using AI.

Users can:
- ask questions about Korean grammar
- learn vocabulary with examples
- practice TOPIK reading questions
- receive AI explanations instead of simple database outputs

---

# ✨ Main Features

## 1. Grammar & Vocabulary AI Assistant

Users can ask questions like:

- "How to express future tense?"
- "What does -(으)ㄹ 거예요 mean?"
- "Explain the difference between 은/는 and 이/가"

The AI provides:
- grammar explanations
- translations
- examples
- usage tips

---

## 2. TOPIK Reading Practice

Users can practice TOPIK-style reading questions.

The system can:
- generate reading questions from the database
- provide multiple choice answers
- check user answers
- explain correct answers

---

# 🧠 Technologies Used

## Backend
- Python
- FastAPI

## AI / NLP
- OpenAI API
- Sentence Transformers
- RAG (Retrieval-Augmented Generation)

## Database
- ChromaDB (Vector Database)

## Frontend
- Streamlit / React (in progress)

---

# 📂 Project Structure

```bash
AI_Korea/
│
├── backend/           # Backend API
├── data/              # CSV datasets
├── scripts/           # Python scripts
├── vector_db/         # ChromaDB vector storage
├── frontend/          # Frontend UI
├── docs/              # Documentation
│
├── requirements.txt
└── README.md
