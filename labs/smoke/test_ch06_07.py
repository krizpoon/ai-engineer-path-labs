"""Chapters 6–7 run for real: MiniLM tokenizer and embeddings, a cross-encoder and Chroma.

They need requirements-ml.txt and download about 200 MB of models on the first run.
Only the calls to Claude go to the fake server.
"""
import re

from conftest import needs_ml, offline_only
from fake_claude import text

pytestmark = needs_ml


def test_ch06_semantic_search_ranks_by_meaning(lab):
    out = lab(6).run("semantic_search.py").stdout
    assert out.splitlines()[0].endswith("recover access to your account if you forget your login.")


def test_ch06_chunker_tests(lab):
    lab(6).run("-m", "pytest", "-q", "-p", "no:cacheprovider", "test_chunker.py")


def test_ch06_chunk_docs(lab):
    ch6 = lab(6)
    ch6.add("ch06/handbook.md")
    out = ch6.run("chunk_docs.py").stdout
    assert out.startswith("256\n") and "chunks" in out


def test_ch06_truncation_demo(lab):
    out = lab(6).run("truncation_demo.py").stdout
    values = [float(v) for v in re.findall(r"-?\d+\.\d+", out)]
    same, whole, best = values[0], values[1], values[2]
    assert same > 0.99, "the last sentence should be cut off before embedding"
    assert best > whole, "the chunk holding the rule should match the question better"


def test_ch06_chroma_and_rrf(lab):
    ch6 = lab(6)
    assert "recover access" in ch6.run("chroma_store.py").stdout
    assert ch6.run("rrf.py").stdout.strip() == "['faq-2', 'faq-7', 'faq-4', 'faq-9']"


def test_ch07_ingest_check(lab):
    out = lab(7).run("ingest_check.py").stdout
    assert "ingestion check passed" in out


def test_ch07_retrieval_eval_unit_tests(lab):
    lab(7).run("-m", "pytest", "-q", "-p", "no:cacheprovider", "test_retrieval_eval.py")


def test_ch07_ingest_search_rerank_and_eval(lab):
    ch7 = lab(7)
    ch7.add("ch07/handbook")
    assert re.search(r"^\d+ chunks indexed", ch7.run("ingest.py").stdout, re.M)

    # Real Chroma filter: the restricted case would raise if pay.md leaked.
    out = ch7.run("retrieval_eval.py").stdout
    assert "search           hit rate@5 100%  recall@5 100%" in out
    assert "search + rerank  hit rate@5 100%  recall@5 100%" in out

    hits = ch7.run("-c", "from answer import search\n"
                   "for g in (['everyone'], ['everyone', 'managers']):\n"
                   "    print(sorted({h['source'] for h in search('pay bands', g)}))").stdout
    everyone, managers = hits.splitlines()
    assert "managers/pay.md" not in everyone and "managers/pay.md" in managers


@offline_only
def test_ch07_answer_sends_only_permitted_documents(lab):
    ch7 = lab(7)
    ch7.add("ch07/handbook")
    ch7.run("ingest.py")
    out = ch7.run("answer.py", reply=lambda r: text("26 weeks (handbook/everyone/leave.md)")).stdout
    assert "26 weeks" in out
    prompt = ch7.fake.requests[0]["messages"][0]["content"]
    assert 'source="handbook/everyone/leave.md"' in prompt and "managers" not in prompt


def cited(request):
    """A reply citing the first document sent, as the citations feature does."""
    doc = request["messages"][0]["content"][0]
    quote = doc["source"]["data"][:40]
    return text("Refunds take 5 working days.", citations=[{
        "type": "char_location", "cited_text": quote, "document_index": 0,
        "document_title": doc["title"], "start_char_index": 0, "end_char_index": len(quote)}])


@offline_only
def test_ch07_citations(lab):
    ch7 = lab(7)
    ch7.add("ch07/handbook")
    ch7.run("ingest.py")
    out = ch7.run("citations.py", reply=cited).stdout
    assert out.startswith("Refunds take 5 working days. [handbook/everyone/")


@offline_only
def test_ch07_contextualise_caches_the_document(lab):
    ch7 = lab(7)
    out = ch7.run("-c", "from contextualise import contextualise\n"
                  "print(contextualise('Whole doc.', 'A chunk.'))",
                  reply=lambda r: text("From the refunds policy.")).stdout
    assert out.strip().endswith("A chunk.") and out.startswith("From the refunds policy.")
    assert ch7.fake.requests[0]["system"][0]["cache_control"] == {"type": "ephemeral"}
