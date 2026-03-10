# 📄 Resume Tool

AI-powered resume cleanup and formatting. Paste your resume, get instant suggestions and an improved version.

## Features

- **AI Analysis** — GPT-4o-mini reviews your resume for content, formatting, language, impact, and ATS compatibility
- **Priority Suggestions** — Color-coded (high/medium/low) improvement recommendations with examples
- **Improved Version** — Get a rewritten version incorporating all high-priority fixes
- **Dark UI** — Clean, mobile-friendly dark interface
- **Copy to Clipboard** — One-click copy of the improved resume

## Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/jabreeflor/resume-tool&env=OPENAI_API_KEY)

Or manually:
```bash
npm i -g vercel
vercel --prod
```

Set `OPENAI_API_KEY` in Vercel environment variables.

## Run Locally

```bash
git clone https://github.com/jabreeflor/resume-tool.git
cd resume-tool
npm install
cp .env.example .env.local
# Add your OpenAI API key to .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Tech Stack

- Next.js 14 (App Router)
- Tailwind CSS
- OpenAI GPT-4o-mini
- Vercel deployment

## License

MIT
