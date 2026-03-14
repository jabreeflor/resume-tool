#!/usr/bin/env python3
"""
resume-tool — AI-powered resume editor CLI
Uses Gemini API for improvement suggestions.

Commands:
  resume parse <pdf>         Extract content from a PDF resume
  resume improve <pdf>       Get AI-powered improvement suggestions (Gemini)
  resume export [--pdf|--md] Output polished version as PDF or Markdown
"""

import sys
import os
import json
import re
import argparse
import urllib.request
import urllib.parse
import textwrap
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".resume-tool"
CONFIG_FILE = CONFIG_DIR / "config.json"
GEMINI_API  = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

COLORS = {
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}

def c(color, text):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

def die(msg):
    print(c("red", f"Error: {msg}"), file=sys.stderr)
    sys.exit(1)

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg):
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_api_key():
    cfg = load_config()
    key = cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    if not key:
        die("Gemini API key not set.\n"
            "Run: resume config --gemini-key YOUR_KEY\n"
            "Or: export GEMINI_API_KEY=YOUR_KEY")
    return key

# ── PDF parsing ───────────────────────────────────────────────────────────────
def parse_pdf(path: Path) -> str:
    """Extract text from a PDF resume."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        return "\n".join(pages).strip()
    except ImportError:
        # Fallback: try pdfminer
        try:
            from pdfminer.high_level import extract_text
            return extract_text(str(path)).strip()
        except ImportError:
            die("PDF parsing requires PyMuPDF or pdfminer.six.\n"
                "Run: pip3 install pymupdf\n  OR: pip3 install pdfminer.six")

def extract_sections(text: str) -> dict:
    """Heuristically split resume text into sections."""
    section_headers = [
        "experience", "work experience", "employment", "education",
        "skills", "technical skills", "projects", "certifications",
        "summary", "objective", "contact", "awards", "publications",
        "languages", "interests", "volunteer",
    ]

    lines  = text.split("\n")
    sections = {"header": []}
    current = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        matched = next((h for h in section_headers if lower.startswith(h) or lower == h), None)
        if matched and len(stripped) < 60:
            current = matched
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}

# ── Gemini API ─────────────────────────────────────────────────────────────────
def gemini(prompt: str, api_key: str) -> str:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8192},
    }).encode()

    url = f"{GEMINI_API}?key={api_key}"
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        die(f"Gemini API error: {e}")

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_parse(pdf_path: str):
    path = Path(pdf_path)
    if not path.exists(): die(f"File not found: {pdf_path}")
    if path.suffix.lower() != ".pdf": die("File must be a PDF")

    print(c("cyan", f"\n📄 Parsing: {path.name}\n"))
    text = parse_pdf(path)
    sections = extract_sections(text)

    print(c("bold", "═" * 60))
    for section, content in sections.items():
        print(c("yellow", f"\n▶ {section.upper()}"))
        print(c("dim", "─" * 40))
        # Wrap long lines
        for line in content.split("\n"):
            if len(line) > 100:
                print(textwrap.fill(line, 100, initial_indent="  ", subsequent_indent="  "))
            else:
                print(f"  {line}")
    print(c("bold", "\n" + "═" * 60))
    print(c("dim", f"\n{len(text.split())} words · {len(sections)} sections detected"))

    # Cache parsed content
    cache_path = CONFIG_DIR / "last-parsed.json"
    CONFIG_DIR.mkdir(exist_ok=True)
    cache_path.write_text(json.dumps({
        "source": str(path.absolute()),
        "text": text,
        "sections": sections,
    }, indent=2))
    print(c("dim", f"Cached to {cache_path} — use 'resume export' to generate output"))

def cmd_improve(pdf_path: str, focus: list[str] = None):
    path = Path(pdf_path)
    if not path.exists(): die(f"File not found: {pdf_path}")

    print(c("cyan", f"\n🤖 Analyzing: {path.name}\n"))
    api_key = get_api_key()
    text = parse_pdf(path)

    focus_str = ""
    if focus:
        focus_str = f"\n\nFocus specifically on: {', '.join(focus)}"

    prompt = f"""You are a senior technical recruiter and resume coach.
Analyze this resume and provide:

1. **Overall Assessment** (2-3 sentences)
2. **Top 5 Specific Improvements** — actionable, numbered, with before/after examples
3. **Missing Elements** — what's absent that strong candidates typically include
4. **ATS Optimization** — keywords and formatting tips for Applicant Tracking Systems
5. **Strongest Points** — what's already working well (keep/amplify)
6. **Rewritten Summary** — a polished 3-sentence professional summary based on their background{focus_str}

Be direct and specific. Reference actual content from their resume.

---RESUME START---
{text[:6000]}
---RESUME END---"""

    print(c("dim", "Sending to Gemini... "), end="", flush=True)
    result = gemini(prompt, api_key)
    print(c("green", "done\n"))

    # Pretty print the markdown-ish response
    for line in result.split("\n"):
        if line.startswith("##") or line.startswith("**") and line.endswith("**"):
            print(c("yellow", line))
        elif line.startswith("-") or line.startswith("•"):
            print(c("dim", "  ") + line)
        elif re.match(r"^\d+\.", line):
            print(c("cyan", line))
        else:
            print(line)

    # Save suggestions
    out_path = CONFIG_DIR / "last-suggestions.md"
    CONFIG_DIR.mkdir(exist_ok=True)
    out_path.write_text(f"# Resume Improvement Suggestions\n\nSource: {path}\n\n{result}")
    print(c("dim", f"\nSaved to {out_path}"))

def cmd_export(output_format: str = "md", output_path: str = None):
    """Generate a polished output from the last parsed resume + suggestions."""
    cache_path = CONFIG_DIR / "last-parsed.json"
    if not cache_path.exists():
        die("No parsed resume found. Run 'resume parse <pdf>' first.")

    cache = json.loads(cache_path.read_text())
    text = cache["text"]
    suggestions_path = CONFIG_DIR / "last-suggestions.md"

    api_key = get_api_key()

    has_suggestions = suggestions_path.exists()
    suggestions_text = suggestions_path.read_text() if has_suggestions else ""

    prompt = f"""You are a professional resume writer.
{"Based on these improvement suggestions:" if has_suggestions else ""}
{suggestions_text[:2000] if has_suggestions else ""}

Rewrite the following resume content into a clean, polished, ATS-optimized format.
Output as clean Markdown with clear sections.
Keep all factual information — do NOT invent experience, dates, or skills.
Improve phrasing, remove filler, strengthen bullet points with impact metrics where possible.

---ORIGINAL RESUME---
{text[:5000]}
---END---

Output ONLY the polished resume in Markdown. Start with the name/contact header."""

    print(c("cyan", "\n✍️  Generating polished resume...\n"))
    result = gemini(prompt, api_key)

    # Determine output path
    if not output_path:
        output_path = str(Path.cwd() / f"resume-polished.{output_format}")

    if output_format == "md":
        Path(output_path).write_text(result)
        print(c("green", f"✓ Markdown saved: {output_path}"))

    elif output_format == "pdf":
        # Generate PDF from markdown using reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
            from reportlab.lib import colors

            doc = SimpleDocTemplate(output_path, pagesize=letter,
                rightMargin=0.75*inch, leftMargin=0.75*inch,
                topMargin=0.75*inch, bottomMargin=0.75*inch)
            styles = getSampleStyleSheet()
            story = []

            heading_style = ParagraphStyle("heading", parent=styles["Heading1"],
                fontSize=14, spaceAfter=4)
            h2_style = ParagraphStyle("h2", parent=styles["Heading2"],
                fontSize=12, spaceAfter=4, textColor=colors.HexColor("#2D5BE3"))
            body_style = ParagraphStyle("body", parent=styles["Normal"],
                fontSize=10, spaceAfter=2, leading=14)
            bullet_style = ParagraphStyle("bullet", parent=styles["Normal"],
                fontSize=10, spaceAfter=2, leftIndent=20, leading=14)

            for line in result.split("\n"):
                if line.startswith("# "):
                    story.append(Paragraph(line[2:], heading_style))
                elif line.startswith("## "):
                    story.append(Spacer(1, 6))
                    story.append(Paragraph(line[3:], h2_style))
                    story.append(HRFlowable(width="100%", thickness=0.5,
                        color=colors.HexColor("#2D5BE3")))
                elif line.startswith("- ") or line.startswith("• "):
                    story.append(Paragraph("• " + line[2:], bullet_style))
                elif line.strip():
                    story.append(Paragraph(line, body_style))
                else:
                    story.append(Spacer(1, 4))

            doc.build(story)
            print(c("green", f"✓ PDF saved: {output_path}"))
        except ImportError:
            die("PDF export requires reportlab: pip3 install reportlab")
    else:
        die(f"Unknown format: {output_format}. Use --md or --pdf")

def cmd_config(gemini_key: str = None):
    cfg = load_config()
    if gemini_key:
        cfg["gemini_api_key"] = gemini_key
        save_config(cfg)
        print(c("green", f"✓ API key saved to {CONFIG_FILE}"))
    else:
        print(c("cyan", "\nCurrent config:"))
        if cfg.get("gemini_api_key"):
            key = cfg["gemini_api_key"]
            print(f"  gemini_api_key: {key[:8]}...{key[-4:]}")
        else:
            print(c("yellow", "  gemini_api_key: NOT SET"))
        print(c("dim", f"\nConfig file: {CONFIG_FILE}"))

def usage():
    print(f"""
{c("bold", c("cyan", "resume-tool"))} — AI-powered resume editor

{c("bold", "Commands:")}
  resume parse <pdf>                Extract and display resume content
  resume improve <pdf> [--focus AREA]  AI improvement suggestions (Gemini)
  resume export [--pdf|--md] [-o path]  Generate polished output
  resume config [--gemini-key KEY]  Set Gemini API key

{c("bold", "Setup:")}
  resume config --gemini-key YOUR_GEMINI_KEY

{c("bold", "Workflow:")}
  resume parse my-resume.pdf        # See what was extracted
  resume improve my-resume.pdf      # Get AI suggestions
  resume export --pdf               # Generate polished PDF
  resume export --md                # Generate polished Markdown

{c("bold", "Options:")}
  --focus "keywords,formatting"     Focus improvement on specific areas
  -o, --output path                 Output file path
""")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        usage(); sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "parse":
        if not args: die("Usage: resume parse <pdf>")
        cmd_parse(args[0])

    elif cmd == "improve":
        if not args: die("Usage: resume improve <pdf> [--focus AREA]")
        focus = []
        focus_idx = next((i for i, a in enumerate(args) if a == "--focus"), None)
        if focus_idx is not None and len(args) > focus_idx + 1:
            focus = args[focus_idx + 1].split(",")
        cmd_improve(args[0], focus)

    elif cmd == "export":
        fmt = "pdf" if "--pdf" in args else "md"
        out_idx = next((i for i, a in enumerate(args) if a in ("-o", "--output")), None)
        out = args[out_idx + 1] if out_idx is not None and len(args) > out_idx + 1 else None
        cmd_export(fmt, out)

    elif cmd == "config":
        key_idx = next((i for i, a in enumerate(args) if a == "--gemini-key"), None)
        key = args[key_idx + 1] if key_idx is not None and len(args) > key_idx + 1 else None
        cmd_config(key)

    else:
        usage()

if __name__ == "__main__":
    main()
