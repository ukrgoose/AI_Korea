import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TOPIKMate",
    layout="wide"
)

st.title("TOPIKMate")
st.write("AI assistant for TOPIK preparation")

page = st.sidebar.radio(
    "Choose mode",
    [
        "Grammar & Vocabulary AI",
        "TOPIK Reading Practice",
        "Vocabulary Flashcards"
    ]
)

# =========================
# Grammar & Vocabulary AI
# =========================

if page == "Grammar & Vocabulary AI":

    st.header("Grammar & Vocabulary AI")

    question = st.text_input(
        "Ask anything about Korean grammar or vocabulary:"
    )

    if st.button("Send"):

        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": question}
        )

        if response.status_code == 200:

            answer = response.json()["answer"]

            st.markdown(
                f"""
                <div style="
                    background:#111827;
                    padding:30px;
                    border-radius:20px;
                    border:1px solid #374151;
                    margin-top:20px;
                ">
                    <h3 style="color:white;">Answer</h3>
                    <p style="color:#E5E7EB;font-size:20px;">
                        {answer}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.error("Backend error")


# =========================
# TOPIK Practice
# =========================

if page == "TOPIK Reading Practice":

    st.header("TOPIK Reading Practice")

    question_type = st.selectbox(
        "Choose question type:",
        [
            "grammar_fill_blank",
            "vocabulary_match",
            "short_reading_comprehension",
            "paragraph_fill_blank"
        ]
    )

    if st.button("Get 5 Questions"):

        response = requests.get(
            f"{BACKEND_URL}/practice/questions",
            params={
                "level": "topik_1",
                "question_type": question_type
            }
        )

        if response.status_code == 200:
            st.session_state.questions = response.json()

        else:
            st.error("Backend error")

    if "questions" in st.session_state:

        answers = []

        for q in st.session_state.questions:

            st.markdown("---")

            st.subheader(f"Question {q['number']}")

            st.write(q["text"])
            st.write(q["question"])

            answer = st.radio(
                "Choose your answer:",
                options=list(q["options"].keys()),
                format_func=lambda x, options=q["options"]: f"{x}. {options[x]}",
                key=f"question_{q['id']}"
            )

            answers.append({
                "question_id": q["id"],
                "user_answer": answer
            })

        if st.button("Submit Answers"):

            response = requests.post(
                f"{BACKEND_URL}/practice/check",
                json={"answers": answers}
            )

            if response.status_code == 200:

                data = response.json()

                if data is None:
                    st.error("Backend returned empty result. Check /practice/check in backend.")
                    st.stop()

                if isinstance(data, dict):
                    results = data.get("results", [])
                elif isinstance(data, list):
                    results = data
                else:
                    st.error("Unexpected backend response format.")
                    st.stop()

                if not results:
                    st.error("No results received from backend.")
                    st.stop()

                score = 0

                for result in results:
                    if result.get("is_correct"):
                        score += 1

                st.success(f"Score: {score} / {len(results)}")

                for result in results:

                    st.markdown("---")

                    if result.get("is_correct"):
                        st.success(f"Question {result.get('number')} — Correct")
                    else:
                        st.error(f"Question {result.get('number')} — Wrong")

                    st.write(f"Your answer: {result.get('user_answer')}")
                    st.write(f"Correct answer: {result.get('correct_answer')}")
                    st.write(f"Explanation: {result.get('explanation')}")

            else:
                st.error(f"Backend error: {response.status_code}")
                st.write(response.text)

# =========================
# Vocabulary Flashcards
# =========================

if page == "Vocabulary Flashcards":

    st.header("Vocabulary Flashcards")

    level = st.selectbox(
        "Choose TOPIK level:",
        ["TOPIK I", "TOPIK II"]
    )

    if st.button("Load Flashcards"):

        response = requests.get(
            f"{BACKEND_URL}/vocab/flashcards",
            params={
                "level": level,
                "count": 10
            }
        )

        if response.status_code == 200:

            st.session_state.flashcards = response.json()
            st.session_state.card_index = 0
            st.session_state.show_answer = False
            st.session_state.show_examples = False

        else:
            st.error("Backend error")

    if "flashcards" in st.session_state:

        cards = st.session_state.flashcards
        index = st.session_state.card_index
        card = cards[index]

        st.write(f"Card {index + 1} of {len(cards)}")

        progress = (index + 1) / len(cards)
        st.progress(progress)

        st.markdown(
            """
<style>

.flashcard {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    border-radius: 32px;
    padding: 100px 50px;
    text-align: center;
    margin-top: 30px;
    margin-bottom: 30px;
    box-shadow: 0 20px 40px rgba(79,70,229,0.25);
}

.korean-word {
    color: white;
    font-size: 78px;
    font-weight: 800;
    margin-bottom: 20px;
}

.meaning {
    color: white;
    font-size: 64px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hint {
    color: rgba(255,255,255,0.75);
    font-size: 20px;
}

.small-label {
    color: rgba(255,255,255,0.8);
    font-size: 18px;
    letter-spacing: 1px;
}

.example-box {
    background: #111827;
    border: 1px solid #374151;
    padding: 30px;
    border-radius: 20px;
    margin-top: 20px;
}

.example-korean {
    color: white;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
}

.example-translation {
    color: #D1D5DB;
    font-size: 20px;
}

</style>
            """,
            unsafe_allow_html=True
        )

        if not st.session_state.show_answer:

            flashcard_html = f"""
<div class="flashcard">
    <div class="korean-word">{card['word']}</div>
    <div class="hint">Click Show Answer to reveal the meaning</div>
</div>
"""

        else:

            flashcard_html = f"""
<div class="flashcard">
    <div class="meaning">{card['meaning']}</div>
    <div class="small-label">Meaning</div>
</div>
"""

        st.markdown(
            flashcard_html,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            if st.button("Previous Card"):

                if st.session_state.card_index > 0:

                    st.session_state.card_index -= 1
                    st.session_state.show_answer = False
                    st.session_state.show_examples = False
                    st.rerun()

        with col2:

            if st.button("Show Answer"):

                st.session_state.show_answer = True
                st.rerun()

        with col3:

            if st.button("Hide Answer"):

                st.session_state.show_answer = False
                st.session_state.show_examples = False
                st.rerun()

        with col4:

            if st.button("Show Examples"):

                st.session_state.show_examples = (
                    not st.session_state.show_examples
                )

                st.rerun()

        with col5:

            if st.button("Next Card"):

                if st.session_state.card_index < len(cards) - 1:

                    st.session_state.card_index += 1
                    st.session_state.show_answer = False
                    st.session_state.show_examples = False
                    st.rerun()

                else:
                    st.success("Finished all flashcards!")

        if st.session_state.show_examples:

            st.markdown(
                f"""
<div class="example-box">
    <div class="example-korean">{card['example']}</div>
    <div class="example-translation">{card['translation']}</div>
</div>
""",
                unsafe_allow_html=True
            )