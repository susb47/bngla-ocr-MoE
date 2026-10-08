# Runbook – Milestone 4 (read-only review)

## Prerequisites (once)

```bash
cd moe-docs

# Python
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Frontend
cd src/moedocs/review/web
npm install
cd ../../../../