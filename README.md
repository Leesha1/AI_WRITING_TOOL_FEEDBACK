# AI Writing Feedback Tool

A Streamlit web app that evaluates text using two approaches side by side:
1. **Flesch Reading Ease** — a classic NLP formula, instant and free (no API call)
2. **LLM-based evaluation** — clarity score, tone, grammar issues, and suggestions via Gemini API

## Why both?
Formulas are fast and deterministic but can't judge tone or coherence. LLMs can make
that judgment call but cost an API call and are slower. This project deliberately uses
each where it's actually the better tool.

## Tech stack
Python, Streamlit, Google Gemini API (google-genai SDK), textstat

## How to run
1. `pip install streamlit google-genai textstat`
2. Add your Gemini API key in the code (or via Streamlit secrets)
3. `streamlit run project3_app.py`

## What I'd improve next
- Move the API key to Streamlit's secrets management instead of hardcoding
- Add batch processing for multiple texts at once
- Add support for uploading a file directly instead of pasting text
