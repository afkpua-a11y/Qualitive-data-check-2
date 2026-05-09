# Qualitive-data-check-2

A program that checks validation claims for qualitative data and Grounded Theory prompts after analysis.

## Validator API

Run the API locally:

```bash
uvicorn app:app --reload
```

Then submit validation requests to `POST /validate` with document text, a document URL, or a local path plus a list of claims.

## Kronespillet

This project now also includes a digital version of **Kronespillet** for learning probability and event trees.

Start the FastAPI app and open:

```text
http://127.0.0.1:8000/kronespillet
```

The game lets you drag and release a digital coin, tracks balance, rounds and wins, and explains the outcomes with a probability distribution and a simple hendelsestre. The front page redirects to the game so it is easy to find during a presentation.
