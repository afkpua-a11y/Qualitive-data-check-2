import argparse, json
from pathlib import Path
import pandas as pd
from validator_lib import validate_file

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--terms")
    group.add_argument("--claims")
    ap.add_argument("--context", type=int, default=120)
    ap.add_argument("--substring", action="store_true")
    ap.add_argument("--case-sensitive", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.terms:
        items = [{"id": f"t{i+1}", "text": t.strip()} for i, t in enumerate(args.terms.split(";")) if t.strip()]
    else:
        items = json.loads(Path(args.claims).read_text(encoding="utf-8"))

    options = {
        "whole_word": not args.substring,
        "case_insensitive": not args.case_sensitive,
        "context": args.context,
    }

    result = validate_file(args.doc, items, options)
    rows = []
    for r in result["results"]:
        if r["hits"]:
            for h in r["hits"]:
                rows.append({
                    "claim_id": r["claim_id"],
                    "term": r["term"],
                    "status": r["status"],
                    "count": r["count"],
                    "page": h["page"],
                    "offset": h["offset"],
                    "context": h["context"],
                })
        else:
            rows.append({
                "claim_id": r["claim_id"],
                "term": r["term"],
                "status": r["status"],
                "count": r["count"],
                "page": None,
                "offset": None,
                "context": None,
            })

    df = pd.DataFrame(rows)
    out_path = args.out or f"results_{Path(args.doc).stem}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Saved details to: {out_path}")

if __name__ == "__main__":
    main()
