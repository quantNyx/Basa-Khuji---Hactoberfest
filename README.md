# 🏠 Basa Khuji AI

**Decode Dhaka to-let listings with Gemma, then practise the call with a grumpy Bariwala.**

Finding a *basa* in Dhaka means vague listings ("5 min from Metro" is often 2.5 km), hidden costs, advance-payment scams, and landlords who turn away bachelors and students. Basa Khuji AI helps both sides of the market: tenants decode any listing, and landlords post their flats for free.

Built for the **Hacktoberfest Dhaka Hackathon** with **Gemma**, Google's open model.

## Features
- **Reality Report.** Paste a listing or upload a To-Let sign photo. Gemma returns a Bachelor Survival Score, a verdict, "what they wrote vs. what it means in Dhaka", and the real monthly cost including hidden extras.
- **Phone script.** A polite Banglish script written for university students.
- **Bariwala Boss Fight.** A roleplay with a simulated landlord. Polite, honest answers raise Uncle's patience; the wrong answers drop it.
- **Landlord posting.** Landlords add a flat (rent, area, floor, tenant preference, photo, phone) and tenants can run any posted flat through the AI with one click.
- **Gemma first, Gemini fallback.** Defaults to Gemma; a header switch lets you try Gemini, and the app falls back to the other model if one is rate-limited. The header shows which model answered.

## Tech stack
Python, Flask, SQLite, vanilla JavaScript, Gemma via the Google AI Studio (Gemini) API.

## How it works
1. `system_prompt.txt` defines the persona and a two-mode state machine: first message is the decoder, every follow-up is the boss fight.
2. Gemma on this API has no system-instruction field, so the prompt is sent inside the first user turn. The browser keeps the chat history and sends it with each request.
3. The front end turns the model's Markdown into the score ring, verdict stamp, receipt and call card, so the prompt's headings must stay unchanged.

## Run locally
```bash
git clone https://github.com/YOUR_USERNAME/basa-khuji-ai.git
cd basa-khuji-ai
cp .env.example .env        # then put your key in .env (Windows: copy the file manually)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8000. Windows users can double-click `run.bat`. Without a key the app starts in demo mode with a canned report.

Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | none | Google AI Studio key, works for Gemma and Gemini |
| `GEMMA_MODEL` | `gemma-3-27b-it` | Gemma model name |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Fallback model name |
| `DB_PATH` | `basa.db` | Where listings are stored |
| `PORT` | `8000` | Server port |

## Deploy (Render, free)
1. Push this repo to GitHub.
2. On [render.com](https://render.com): New, then Blueprint, pick the repo, Apply.
3. Paste `GEMINI_API_KEY` when asked. Open the `onrender.com` link once it's live.

Note: on Render's free plan the SQLite file resets when the service restarts, so posted flats are not permanent. Use a managed database for production.

## Project structure
```
app.py              Flask server, listings API, Gemma/Gemini calls
system_prompt.txt   Persona and output format
static/index.html   Single-page UI
render.yaml         One-click Render deploy
Procfile            gunicorn start command
```

## Limitations
- Hidden-cost figures are the model's estimates based on Dhaka patterns, not verified market data.
- Listings are not moderated or verified, and phone numbers are public by design.
- Basa Khuji AI is a prototype and not a substitute for checking a flat in person.

## Roadmap
- Read handwritten Bangla signs
- Real area rent data for more accurate estimates
- Landlord-side check that flags missing details before a listing goes live
- Permanent database, accounts and moderation
- Self-hosted Gemma option, so no API key is needed

## Team
Md. Sakib Al Hasan, NITER. Add teammates here.

## License
MIT
