# Qualitive-data-check-2
A Program that checks for validation - Grounded Theory - on ChatGPT promts, after analysis.

## GPT Interface
`gpt_interface.py` can fetch a document from GitHub or a local path, validate claims using the existing `validator_lib`, and optionally ask an OpenAI model to review the results.

### Basic usage
```bash
python gpt_interface.py --local-path README.md --claims sample/claims.json
```

### With GPT validation
Install the `openai` package and set your API key in `OPENAI_API_KEY`:
```bash
pip install openai
export OPENAI_API_KEY=your_key
python gpt_interface.py --local-path README.md --claims sample/claims.json --use-gpt
```
