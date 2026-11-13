from __future__ import annotations

import importlib.util
import os
import re


def model_status() -> dict[str, bool]:
    return {"dependencies_installed": importlib.util.find_spec("sumy") is not None and importlib.util.find_spec("nltk") is not None, "loaded": True}


class FrenchTokenizer:
    """Small French tokenizer that needs no downloaded NLTK corpora."""
    def __init__(self):
        from nltk.tokenize import TreebankWordTokenizer
        self.words = TreebankWordTokenizer()

    def to_sentences(self, paragraph: str) -> tuple[str, ...]:
        text = re.sub(r"\s+", " ", paragraph).strip()
        if not text:
            return ()
        parts = re.split(r"(?<=[.!?\u2026])\s+(?=[A-Z\u00c0-\u00de0-9\u00ab\"\u201c])", text)
        return tuple(part.strip() for part in parts if part.strip())

    def to_words(self, sentence: str) -> tuple[str, ...]:
        from sumy.nlp.tokenizers import Tokenizer
        return tuple(word for word in self.words.tokenize(sentence) if Tokenizer._is_word(word))


def summarize_with_sumy(text: str, length: str) -> tuple[str, int]:
    from sumy.nlp.stemmers import Stemmer
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.utils import get_stop_words
    from app.summarizer import split_text

    limits = {"court": (5, 3), "moyen": (12, 5), "detaille": (24, 8)}
    if length not in limits:
        raise ValueError("Longueur de resume non reconnue.")
    final_count, per_section = limits[length]
    chunks = split_text(text, int(os.getenv("CHUNK_CHARS", "36000")))
    tokenizer, stemmer = FrenchTokenizer(), Stemmer("french")
    summaries = []
    for chunk in chunks:
        sentences = tokenizer.to_sentences(chunk)
        if not sentences:
            continue
        if len(sentences) <= per_section:
            summaries.extend(sentences)
            continue
        parser = PlaintextParser.from_string(chunk, tokenizer)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("french")
        try:
            summaries.extend(str(sentence) for sentence in summarizer(parser.document, per_section))
        except (ValueError, ZeroDivisionError):
            summaries.extend(sentences[:per_section])
    if not summaries:
        raise ValueError("Aucune phrase exploitable n'a ete trouvee dans ce document.")
    if len(summaries) > final_count:
        parser = PlaintextParser.from_string("\n".join(summaries), tokenizer)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("french")
        try:
            summaries = [str(sentence) for sentence in summarizer(parser.document, final_count)]
        except (ValueError, ZeroDivisionError):
            summaries = summaries[:final_count]
    return " ".join(summaries), len(chunks)
