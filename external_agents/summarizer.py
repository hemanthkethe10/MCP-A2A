import os
import logging
from typing import Optional
import PyPDF2
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("external_agents.summarizer")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")


def extract_text_from_pdf(pdf_path: str) -> str:
    logger.info(f"Extracting text from PDF: {pdf_path}")
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
        return ""

def simple_summarize(text: str, max_sentences: int = 3) -> str:
    logger.info("Using simple summarizer.")
    sentences = text.split(".")
    summary = ".".join(sentences[:max_sentences])
    return summary.strip()

def openai_summarize(text: str) -> Optional[str]:
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set; cannot use OpenAI summarizer.")
        return None
    logger.info("Using OpenAI API for summarization.")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Summarize the following text."},
            {"role": "user", "content": text[:4000]}  # Truncate for token limit
        ],
        "max_tokens": 256
    }
    try:
        resp = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API summarization failed: {e}")
        return None

def summarize_pdf(pdf_path: str) -> str:
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return "Could not extract text from PDF."
    summary = openai_summarize(text)
    if summary:
        return summary
    return simple_summarize(text) 