"""
PROJECT 3 (FINISHED VERSION): AI Writing Feedback Tool
Run with: streamlit run project3_app.py

WHAT'S NEW vs the basic script:
1. Real web UI (Streamlit) instead of typing into a terminal
2. A second, NON-AI metric (Flesch Reading Ease) shown alongside the
   LLM's score - proves you know when a formula is better than an LLM
   (instant, free, deterministic - no API call needed for this part)
3. Proper error handling for empty input and API failures
4. Clean layout - looks like a real tool, not a script

SETUP:
pip install streamlit google-genai textstat
Then run: streamlit run project3_app.py
(NOT "python project3_app.py" - Streamlit apps are launched differently)
"""

import streamlit as st
from google import genai
import json
import textstat

# ---- SETUP ----
client = genai.Client(api_key="you api key here")
MODEL_NAME = "gemini-flash-latest"


def get_ai_feedback(text: str) -> dict:
    """Sends text to the LLM and asks for structured JSON feedback."""
    prompt = f"""
You are a writing evaluator. Analyze the following text and return ONLY
a valid JSON object (no markdown, no explanation, no code fences) with
this exact structure:

{{
  "clarity_score": <integer 1-10>,
  "grammar_issues": [<list of specific issues found, empty list if none>],
  "tone": "<one word describing the tone>",
  "suggestions": [<list of 2-3 concrete improvement suggestions>]
}}

Text to evaluate:
\"\"\"{text}\"\"\"

Return ONLY the JSON object, nothing else.
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    raw_output = response.text.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json", "", 1).strip()

    return json.loads(raw_output)


def get_readability_metrics(text: str) -> dict:
    """
    Computes readability using the Flesch Reading Ease formula -
    a classic NLP metric that needs NO AI call at all. Deterministic,
    instant, and free. This is the 'when NOT to use an LLM' talking point.
    """
    return {
        "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 1),
        "grade_level": textstat.text_standard(text, float_output=False),
        "word_count": len(text.split()),
        "sentence_count": textstat.sentence_count(text),
    }


# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="AI Writing Feedback Tool", page_icon="✍️")
st.title("✍️ AI Writing Feedback Tool")
st.caption("Combines an LLM-based evaluation with a classic readability formula (Flesch Reading Ease).")

text_input = st.text_area(
    "Paste your text below:",
    height=200,
    placeholder="Paste a paragraph, email, or story excerpt here...",
)

if st.button("Analyze"):
    if not text_input.strip():
        st.warning("Please paste some text first — empty input can't be evaluated.")
    elif len(text_input.split()) < 5:
        st.warning("That's a bit short for meaningful feedback — try at least a full sentence or two.")
    else:
        col1, col2 = st.columns(2)

        # ---- Non-AI metrics (instant, no API call) ----
        with col1:
            st.subheader("📊 Readability (formula-based)")
            with st.spinner("Computing..."):
                metrics = get_readability_metrics(text_input)
            st.metric("Flesch Reading Ease", metrics["flesch_reading_ease"])
            st.write(f"**Estimated grade level:** {metrics['grade_level']}")
            st.write(f"**Word count:** {metrics['word_count']}")
            st.write(f"**Sentence count:** {metrics['sentence_count']}")

        # ---- AI-based metrics (needs an API call) ----
        with col2:
            st.subheader("🤖 AI Evaluation")
            try:
                with st.spinner("Asking the model..."):
                    ai_result = get_ai_feedback(text_input)
                st.metric("Clarity score (1-10)", ai_result["clarity_score"])
                st.write(f"**Tone:** {ai_result['tone']}")
                if ai_result["grammar_issues"]:
                    st.write("**Grammar issues:**")
                    for issue in ai_result["grammar_issues"]:
                        st.write(f"- {issue}")
                else:
                    st.write("**Grammar issues:** None found")
                st.write("**Suggestions:**")
                for s in ai_result["suggestions"]:
                    st.write(f"- {s}")
            except json.JSONDecodeError:
                st.error("The model didn't return valid JSON this time — try again.")
            except Exception as e:
                st.error(f"Something went wrong reaching the AI model: {e}")

        st.divider()
        st.caption(
            "Notice: readability score appears instantly with no API call, "
            "while the AI evaluation needs a round-trip to the model. "
            "This is a real design choice in production tools - use the cheap, "
            "fast, deterministic method when it's good enough, and reserve the "
            "LLM call for judgment calls a formula can't make (tone, coherence, "
            "phrasing quality)."
        )
