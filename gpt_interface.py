import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.request import urlopen
from validator_lib import validate_doc_text, extract_text_from_path

try:
    import openai
except ImportError:  # pragma: no cover - openai is optional
    openai = None

def fetch_github_file(raw_url: str) -> str:
    """Fetch the contents of a raw GitHub file URL as text."""
    with urlopen(raw_url) as resp:
        return resp.read().decode("utf-8")

def validate_document(
    doc_text: str,
    claims: List[Dict[str, str]],
    options: Optional[Dict[str, Any]] = None,
    use_gpt: bool = False,
    model: str = "gpt-3.5-turbo",
) -> Dict[str, Any]:
    """Validate claims locally and optionally via an OpenAI model."""
    results = validate_doc_text(doc_text, claims, options)
    gpt_answer = None
    if use_gpt:
        if openai is None:
            raise RuntimeError("openai package is required for GPT validation")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        openai.api_key = api_key
        prompt = (
            "You are verifying if the following claims are supported by the provided document text.\n"
            "Respond for each claim with 'match' or 'no_match'.\n\n"
            f"Document:\n{doc_text[:4000]}\n\nClaims:\n" +
            "\n".join(f"{c['id']}: {c['text']}" for c in claims)
        )
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        gpt_answer = resp["choices"][0]["message"]["content"].strip()
    return {"results": results, "gpt_response": gpt_answer}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Validate a document and optionally consult GPT")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--raw-url", help="Raw GitHub URL to the document")
    src.add_argument("--local-path", help="Path to a local document")
    ap.add_argument("--claims", required=True, help="Path to JSON file containing claims")
    ap.add_argument("--use-gpt", action="store_true", help="Consult GPT for validation")
    args = ap.parse_args()

    if args.raw_url:
        doc_text = fetch_github_file(args.raw_url)
    else:
        doc_text, _ = extract_text_from_path(args.local_path)

    claims = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    out = validate_document(doc_text, claims, use_gpt=args.use_gpt)
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
