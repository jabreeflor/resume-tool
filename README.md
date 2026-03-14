# resume-tool

AI-powered resume editor CLI. Parse PDFs, get Gemini improvement suggestions, export polished versions.

## Install

```bash
git clone https://github.com/jabreeflor/resume-tool
cd resume-tool
pip3 install -r requirements.txt
chmod +x resume.py
ln -s $(pwd)/resume.py /usr/local/bin/resume  # optional: make global
```

## Setup

```bash
resume config --gemini-key YOUR_GEMINI_API_KEY
# or: export GEMINI_API_KEY=your-key
```

## Workflow

```bash
# 1. Parse — see what's extracted
resume parse my-resume.pdf

# 2. Improve — get AI suggestions
resume improve my-resume.pdf

# Optional: focus on specific areas
resume improve my-resume.pdf --focus "keywords,bullet points,summary"

# 3. Export — generate polished output
resume export --pdf           # → resume-polished.pdf
resume export --md            # → resume-polished.md
resume export --pdf -o final.pdf
```

## Commands

| Command | Description |
|---|---|
| `resume parse <pdf>` | Extract and display resume content by section |
| `resume improve <pdf>` | Gemini AI improvement suggestions (actionable, with examples) |
| `resume export [--pdf\|--md]` | Generate polished version from last parsed + suggestions |
| `resume config --gemini-key KEY` | Set Gemini API key |

## What `improve` gives you

1. Overall assessment
2. Top 5 specific improvements with before/after examples
3. Missing elements
4. ATS optimization tips
5. Strongest points to keep
6. Rewritten professional summary

## Dependencies

- `pymupdf` — PDF text extraction
- `reportlab` — PDF generation for export
- Gemini API (free tier works)
