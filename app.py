from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import httpx
from validator_lib import validate_doc_text, extract_text_from_path

app = FastAPI(title="Validator API", version="1.0.0")

class Claim(BaseModel):
    id: str
    text: str

class ValidateReq(BaseModel):
    doc_text: Optional[str] = None
    doc_url: Optional[HttpUrl] = None
    local_path: Optional[str] = None
    claims: List[Claim]
    options: Dict[str, Any] = {}

@app.post("/validate")
async def validate(req: ValidateReq):
    text = None
    page_texts = None
    if req.doc_text:
        text = req.doc_text
    elif req.local_path:
        text, page_texts = extract_text_from_path(req.local_path)
    elif req.doc_url:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(str(req.doc_url))
            if r.status_code != 200:
                raise HTTPException(status_code=400, detail="Could not download doc_url")
            text = r.text
    else:
        raise HTTPException(status_code=400, detail="Provide doc_text, doc_url, or local_path")

    results = validate_doc_text(text, [c.dict() for c in req.claims], req.options, page_texts)
    return {"results": results, "used_options": req.options}
