# Gold pages for OCR benchmark

Place hand-corrected pairs here:

| File | Description |
|------|-------------|
| `page001.png` | Page image (from normalize or scan) |
| `page001.txt` | Ground-truth UTF-8 text (human corrected) |

Then run:

```bash
PYTHONPATH=src python bench/run_bench.py
```

Metrics reported: **CER**, **WER**, **Conjunct Error Rate**.
