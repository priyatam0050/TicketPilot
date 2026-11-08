# TicketPilot

An IT support ticket assistant, built from scratch in Python, one version at a time.

**End goal:** pass in a ticket's details, and AI sets the priority and auto-assigns it to the right team.

---

## Current version: v1.0

**AI classifies every ticket.** Type a ticket title and an AI model (Google Gemini) suggests the **category** and **priority**, with a one-line **reason**. You can accept it with Enter or override it. Imported tickets are classified automatically too.

### Features

- **AI-assisted Create**: the AI suggests category, priority and reason, and you accept with Enter or type your own priority (a human always has the final say)
- **AI-classified Import**: tickets pulled from an API are classified one by one, with progress (`Classifying : 3/5`)
- **Structured AI output**: the AI must reply in a fixed JSON shape (category, priority, reason), checked by Pydantic, so the program never has to guess at free text
- **Retry with backoff**: if the AI is busy or unreachable, TicketPilot retries 3 times (waiting 2s, 4s, 8s), then falls back safely
- **Safe fallback**: if the AI is unavailable, the ticket is still created as `Unclassified` with priority P4, and nothing crashes
- **Auto-numbering**: `INC0000001`, `INC0000002`, …
- **View, Filter by priority, Search** by keyword, all showing the category
- **Close** a ticket (with "not found" and "already closed" checks)
- **Report**: ticket counts by priority, status and category (SQL `GROUP BY`)
- **SQLite storage** and **settings in `.env`**
- **Input validation**: empty titles and invalid priorities are re-asked, never crash

### Demo

```
Please enter Title
unable to book meeting room from outlook
ASKING AI ...
AI Suggests Category = Software, Priority = P3 , Reason = An application feature (meeting room booking in Outlook) is failing, but the user is not completely blocked from working.
Please enter to accept AI Priority or Type P1-P4 to Overide
p2
INC0000113 Created Succesfully
```

When the AI is unavailable:

```
ASKING AI ...
AI error .... Retrying in 2s...
AI error .... Retrying in 4s...
AI error .... Retrying in 8s...
AI Unavailable after 3 tries
AI unavailable, default priority P4
```

```
--- Tickets by Category ---
Access : 3
Hardware : 1
Software : 12
Unclassified : 102
```

<!-- Add a screenshot here: ![TicketPilot demo](screenshot.png) -->

---

## How accurate is the AI?

I measured it on a labelled test set: tickets where I wrote down the correct answer first, then compared the AI's answer.

| Prompt version | Result |
|---|---|
| First prompt (category names only) | 6/10 |
| Improved prompt (category definitions, ordered rules, priority definitions, examples) | **8/11 overall, category correct on 11/11** |

All 3 misses were **P3 tickets marked P2**. The AI reads "a user is blocked" from the title but can't see whether a workaround exists. That's the line between P2 and P3, and humans often disagree on it too. The human override in Create exists for exactly this.

Run the evaluation yourself with `python llm.py`.

---

## How to run

Requires **Python 3** and a free **Gemini API key** from [Google AI Studio](https://aistudio.google.com/).

```bash
# 1. Get the code
git clone https://github.com/priyatam0050/TicketPilot.git
cd TicketPilot

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the packages
pip install -r requirements.txt

# 4. Create your settings file, then put your API key in it
cp .env.example .env

# 5. Run
python3 main.py
```

### Settings (`.env`)

| Setting | What it does | Default |
|---|---|---|
| `GEMINI_API_KEY` | Your Gemini API key (keep it secret) | none, required |
| `GEMINI_MODEL` | Which Gemini model classifies tickets | none, required |
| `API_URL` | Where tickets are imported from | `https://jsonplaceholder.typicode.com/posts` |
| `DB_NAME` | Database file name | `ticketpilot.db` |
| `IMPORT_LIMIT` | How many items to import | `20` |

`.env` is never committed. `.env.example` is the template.

---

## Project structure

```
TicketPilot/
├── main.py            # Menu: takes user input, asks the AI, calls TicketStore
├── llm.py             # Talks to Gemini: system instruction, classification, retry, evaluation
├── models.py          # Ticket (one ticket) and TicketStore (SQLite storage)
├── importer.py        # Fetches posts from the API, classifies them, maps them to tickets
├── schema.py          # Pydantic models: TicketIn (incoming data), TicketClassification (AI reply)
├── async_demo.py      # Demo: sequential vs async API calls
├── requirements.txt   # Packages needed to run
├── .env.example       # Template for settings
└── .gitignore         # Keeps .env, .venv and database files out of the repo
```

### How it's designed

| Part | Responsibility |
|---|---|
| `Ticket` | One ticket: number, title, priority, status, category, reason. Validates priority. |
| `TicketStore` | The only part that touches the database. |
| `classify_tickets` | The only part that talks to the AI. Returns a checked result, or `None` if it fails. |
| `TicketClassification` | The exact shape the AI must reply in. Uses `Literal` so only the 5 categories and P1–P4 are allowed. |
| `importer.py` | Talks to the outside API and prepares data; it never stores anything itself. |

The AI only **suggests**. `main.py` decides: it shows the suggestion, lets a person override it, and falls back to safe defaults when the AI returns `None`.

---

## Known limitations

- The free Gemini tier has rate limits, so importing many tickets is slow (there's a 2-second pause between calls).
- Imported test data is placeholder Latin text, so its AI categories are guesses. Real ticket titles classify well.
- Priority is decided from the title alone. The AI can't know about workarounds or deadlines unless the title says so.
- Importing twice creates duplicate tickets.
- Tickets created before v1.0 are `Unclassified`.

---

## Roadmap

| Version | What it adds |
|---|---|
| **v0.1** ✅ | Ticket tracker with classes + CSV storage |
| **v0.2** ✅ | SQLite database, API import with validation, report, search, `.env` settings |
| **v1.0** ✅ | **AI sets the priority** and category, with a reason and human override |
| v2.0 | Answers support questions from a knowledge base, with sources (RAG) |
| v3.0 | PostgreSQL + vector search, with measured answer quality |
| v4.0 | **AI agent auto-assigns tickets** to the right team, and escalates to a human when unsure |
| v5.0 | Web API, deployed on the cloud |
| v6.0 | Works with AI assistants through MCP |

---

## What I learned

### v1.0
- Calling an LLM from code (Google Gemini, `google-genai`)
- Writing a **system instruction**: role, category definitions, ordered rules, priority definitions
- **Few-shot prompting**: examples teach the AI the pattern (never reuse test tickets as examples)
- **Structured output**: making the AI reply in JSON that matches a Pydantic model, with `Literal` limiting the allowed values
- **Measuring accuracy** on a labelled test set, reading the AI's reasons to find *why* it missed, then improving the prompt
- **Retry with backoff** for busy servers (503) and rate limits (429), and catching specific errors before general ones
- Designing for failure: the AI returns `None` and the app falls back instead of crashing
- Keeping a **human in the loop**: the AI suggests, a person decides
- Keeping API keys in `.env`, never in code or screenshots

### v0.2
- Calling APIs with `requests`, checking status codes, and handling failures without crashing
- Mapping outside data to my own format (like a transform map)
- Validating incoming data with **Pydantic** models and field validators
- **SQL** with SQLite: `CREATE TABLE`, `INSERT`, `SELECT … WHERE`, `UPDATE`, `GROUP BY`, `LIKE`, `MAX`, `ALTER TABLE`
- Always using `?` placeholders to prevent SQL injection, and `commit()` to save changes
- Virtual environments, `requirements.txt`, and keeping settings in `.env`
- Async basics: `async`/`await` and `asyncio.gather` to run API calls at the same time

### v0.1
- Splitting code across files and importing functions and classes
- `pathlib` for file paths that work on any machine
- Reading and writing CSV files with `DictReader` and `DictWriter`
- `@property` for validation, and `try/except` to handle bad input

---

Built by Preetham Patchipulusu as a learn-by-building project.