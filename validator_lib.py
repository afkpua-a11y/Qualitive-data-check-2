from typing import List, Dict, Any, Optional
from unicodedata import normalize
import regex as re

def norm(txt: str) -> str:
    return normalize("NFKC", txt or "").replace("\u00A0", " ")

def compile_pattern(term: str, whole_word: bool = True, case_insensitive: bool = True):
    t = re.escape(norm(term))
    pat = t if not whole_word else r'(?<!\w)' + t + r'(?!\w)'
    flags = re.IGNORECASE if case_insensitive else 0
    return re.compile(pat, flags)

def find_hits_in_text(text: str, term: str, context: int = 120,
                      whole_word: bool = True, case_insensitive: bool = True):
    text_n = norm(text)
    pat = compile_pattern(term, whole_word, case_insensitive)
    hits = []
    for m in pat.finditer(text_n):
        start, end = m.span()
        s = max(0, start - context)
        e = min(len(text_n), end + context)
        hits.append({
            "offset": start,
            "context": text_n[s:e]
        })
    return hits

def extract_text_from_path(path: str):
    import pathlib
    p = pathlib.Path(path)
    suf = p.suffix.lower()
    if suf == ".pdf":
        import fitz
        doc = fitz.open(p)
        pages = [pg.get_text("text") for pg in doc]
        return "\n".join(pages), pages
    elif suf == ".docx":
        from docx import Document
        doc = Document(p)
        return "\n".join([para.text for para in doc.paragraphs]), None
    else:
        return p.read_text(encoding="utf-8", errors="ignore"), None

def offset_to_page(global_offset: int, page_texts: Optional[list]) -> Optional[int]:
    if not page_texts:
        return None
    acc = 0
    for i, pg in enumerate(page_texts, start=1):
        nxt = acc + len(pg) + 1
        if global_offset < nxt:
            return i
        acc = nxt
    return len(page_texts)

def validate_doc_text(text: str, claims: List[Dict[str, Any]],
                      options: Optional[Dict[str, Any]] = None,
                      page_texts: Optional[list] = None) -> List[Dict[str, Any]]:
    options = options or {}
    whole_word = options.get("whole_word", True)
    case_insensitive = options.get("case_insensitive", True)
    context = int(options.get("context", 120))

    results = []
    for item in claims:
        term = item.get("text", "")
        hits = find_hits_in_text(text, term, context, whole_word, case_insensitive)
        status = "match" if hits else "no_match"
        hit_items = [{
            "offset": h["offset"],
            "page": offset_to_page(h["offset"], page_texts),
            "context": h["context"]
        } for h in hits]
        results.append({
            "claim_id": item.get("id"),
            "term": term,
            "status": status,
            "count": len(hits),
            "hits": hit_items
        })
    return results

def validate_file(file_path: str, claims: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
    text, pages = extract_text_from_path(file_path)
    res = validate_doc_text(text, claims, options, pages)
    return {"doc_path": file_path, "results": res}
