# TicketPilot

An IT support ticket assistant, built from scratch in Python, one version at a time.

**End goal:** pass in a ticket's details, and AI sets the priority and auto-assigns it to the right team.

---

## Current version: v2.0

**TicketPilot now answers support questions from a knowledge base.** Ask a question in plain words and it finds the relevant KB articles by meaning, answers only from them, and cites the article it used. If the knowledge base doesn't cover the question, it says so instead of guessing.

This is Retrieval-Augmented Generation (RAG), built by hand: no framework.

### Features

**New in v2.0**
- **Ask KB**: ask a support question and get an answer with citations like `[KB0001]`
- **Search by meaning**: "internet keeps cutting out in meeting rooms" finds the article titled "Wi-Fi keeps dropping in the office", with no shared keywords needed
- **Grounded answers**: the AI may only use the retrieved articles, so answers contain the company's own details, not generic advice
- **Honest citations**: the Sources line lists only the articles the answer actually cited
- **"I don't know"**: when the KB has no answer, TicketPilot says so and suggests raising a ticket
- **AI checks for similar open tickets** (tool calling): before classifying a new ticket, the AI asks TicketPilot to look up similar open tickets, to spot duplicates and likely outages

**From earlier versions**
- **AI-assisted Create**: the AI suggests category, priority and reason, and you accept or override (a human always has the final say)
- **AI-classified Import**, with structured JSON output checked by Pydantic
- **Retry with backoff** and a safe fallback when the AI is unavailable
- View, Filter, Search, Close, and a Report by priority, status and category
- SQLite storage, settings in `.env`, input validation

### Demo

```
8. ASK KB
Please enter your Question
my vpn shows error 809 at home
Searching KB

To fix VPN Error 809 at home, follow these steps:

1. Open the PVP-SecureConnect client, click the gear icon, and change the gateway
   profile from PVP-Legacy-L2TP to PVP-SSL-ZeroTrust (vpn2.pvpcom.com) [KB0001].
2. Click Connect and approve the push notification in the PVP-Guard MFA app [KB0001].
...
Sources : KB0001
```

```
how long before my password expires
Your password expires after 90 days [KB0008].
Sources : KB0008
```

```
how do I order a new monitor
I don't know. Please raise a ticket.
```

The knowledge base belongs to a made-up company, PVP Corp. Details like `PVP-SecureConnect`, `vpn2.pvpcom.com` and the 90-day rule exist only in these articles, so when an answer contains them, it came from the KB and not from the model's memory.

<!-- Add a screenshot here: ![TicketPilot demo](screenshot.png) -->

---

## How Ask KB works

```
INDEXING (run once, or when the KB changes)
KB articles  ->  chunks (one per section)  ->  embeddings  ->  Chroma

ANSWERING (every question)
question  ->  embedding  ->  5 nearest chunks  ->  prompt with those chunks  ->  answer with [KB] citations
```

1. **Chunking**: each article is split by section (Symptoms, Cause, Steps, If it still fails). The article title is added to every chunk, so each chunk makes sense on its own.
2. **Embeddings**: each chunk is turned into a list of 3072 numbers that represents its meaning. Texts with similar meaning get similar numbers.
3. **Vector store**: chunks, embeddings and KB numbers are saved in Chroma.
4. **Retrieval**: the question is embedded the same way, and Chroma returns the 5 nearest chunks.
5. **Generation**: the chunks are pasted into the prompt, labelled with their KB number. The AI must answer only from them, cite each fact, and say "I don't know" if the answer isn't there.

---

## How well does it work?

### Ask KB (v2.0)

Measured on a labelled test set of 20 questions against a 20-article KB. I wrote each question the way a user would ask it, not the way the article is worded, and decided the expected article before running anything.

| Score | Result | What it measures |
|---|---|---|
| **Retrieval** | **17/17** | Was the expected article among the 5 retrieved chunks? |
| **Answers** | **16/17** | Did the answer cite the expected article? |
| **Refusals** | **3/3** | For questions the KB can't answer, did it say "I don't know"? |

By type of question:

| Type | Example | Answered from the expected article |
|---|---|---|
| Clear (14) | "my trackpad is pushing up and the bottom of my laptop looks bulging" | 14/14 |
| Vague (3) | "printer broken" | 2/3 |
| Not in the KB (3) | "how do I claim travel expenses?" | refused 3/3 |

The one miss was **"printer broken"**. The right article was retrieved, but with only two words to go on, the model couldn't choose between "paper jam" and "add a printer", and answered "I don't know. Please raise a ticket." Scoring retrieval and answers separately is what showed this: the search did its job, and the weak point is very vague questions.

**Results vary a little between runs**, because the model doesn't give the same answer every time. Across several runs, answers were 15–16 out of 17, with a different borderline question missed each time. Retrieval and refusals stayed stable.

Run it yourself with `python rag_eval.py`.

**The evaluation needed debugging too.** Three of the early "misses" were not the AI's fault:

- **A wrong label.** My expected article pointed at the wrong KB number; the search had returned the right one.
- **A duplicate article.** Two KB files contained the same text, and the paper-jam article was missing. The test exposed it: the model kept citing both files for one answer, and no printer question could ever find its article.
- **A strict format check.** The model sometimes wrote `[KB0015, KB0016]` instead of `[KB0015]`, and my check for cited sources missed it. Checks on AI output should be strict about content and forgiving about format.

Other things I found while building it:

- **The chunk that best matches a question isn't always the chunk that answers it.** With 3 results, "VPN error 809" returned the Symptoms and Cause sections but missed the Steps, which held the actual fix. Retrieving 5 chunks instead of 3 fixed it.
- **Keyword search wasn't enough.** In v1.0's similar-ticket lookup, the AI searched for "Wi-Fi" and the SQL `LIKE` didn't match "wifi". With embeddings, "wifi not working" and "I can't get online" share no words and still score 0.90, against about 0.80 for unrelated sentences.

### Ticket classification (v1.0)

| Prompt version | Result |
|---|---|
| First prompt (category names only) | 6/10 |
| Improved prompt (definitions, ordered rules, examples) | **8/11 overall, category correct on 11/11** |

All 3 misses were P3 tickets marked P2: the AI can't see from a title whether a workaround exists. The human override exists for exactly this. Run it with `python llm.py`.

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

# 5. Build the knowledge base index (needed once, and after any KB change)
python3 kb_index.py

# 6. Run
python3 main.py
```

### Settings (`.env`)

| Setting | What it does | Default |
|---|---|---|
| `GEMINI_API_KEY` | Your Gemini API key (keep it secret) | none, required |
| `GEMINI_MODEL` | The model that classifies tickets and writes answers | none, required |
| `EMBED_MODEL` | The model that turns text into embeddings | none, required (`gemini-embedding-001`) |
| `API_URL` | Where tickets are imported from | `https://jsonplaceholder.typicode.com/posts` |
| `DB_NAME` | Database file name | `ticketpilot.db` |
| `IMPORT_LIMIT` | How many items to import | `20` |

`.env` is never committed. `.env.example` is the template.

---

## Project structure

```
TicketPilot/
├── main.py            # Menu: takes user input and calls everything else
├── rag.py             # Ask KB: search_kb (retrieval) and answer_question (answer with citations)
├── rag_eval.py        # 20 labelled test questions: scores retrieval, answers and refusals
├── kb_index.py        # Indexing: chunks the articles, creates embeddings, stores them in Chroma
├── kb_loader.py       # Reads the KB articles from the KB folder
├── KB/                # Knowledge base articles (KB0001.md, ...), one file per article
├── llm.py             # Ticket classification: system instruction, tool calling, retry, evaluation
├── models.py          # Ticket (one ticket) and TicketStore (SQLite storage)
├── importer.py        # Fetches posts from the API, classifies them, maps them to tickets
├── schema.py          # Pydantic models: TicketIn (incoming data), TicketClassification (AI reply)
├── async_demo.py      # Demo: sequential vs async API calls
├── requirements.txt   # Packages needed to run
├── .env.example       # Template for settings
└── .gitignore         # Keeps .env, .venv, the database and the Chroma index out of the repo
```

### How it's designed

| Part | Responsibility |
|---|---|
| `TicketStore` | The only part that touches the ticket database (SQLite). |
| `classify_tickets_with_tools` | Classifies a ticket. The AI can ask for `similar_tickets`; TicketPilot checks the request and runs the lookup itself. |
| `kb_index.py` | Builds the search index. `get_Collection()` is the one place that knows where the Chroma data lives. |
| `search_kb` | Retrieval only: a question in, the nearest chunks out. No AI answer involved. |
| `answer_question` | Builds the prompt from the chunks, asks the AI, and returns the answer with the sources it cited. Always returns the same shape, even on failure. |

Two databases, each for what it's good at: **SQLite** for exact lookups, counts and filters on tickets; **Chroma** for "nearest in meaning" on KB chunks.

The AI never touches either database directly. It only suggests or asks; the code decides what runs.

---

## Known limitations

- **Very vague questions are the weak spot.** On "printer broken", the right article was retrieved but the model refused rather than choose (see the test results). A better behaviour would be to ask one clarifying question when several articles could fit.
- **Answers vary between runs**, so a single test run isn't a stable score. The model is sometimes over-cautious and says "I don't know" on a question it answered correctly in another run.
- **The test set is small** (20 questions), and the expected article for a vague question is partly a judgement call.
- **The index doesn't update itself.** After adding or editing an article, run `python3 kb_index.py` again. Chunks of a deleted article stay in the index until it is rebuilt from scratch.
- **Similar-ticket lookup still uses keyword matching**, so spelling differences ("Wi-Fi" vs "wifi") can hide duplicates.
- The free Gemini tier has rate limits, so importing many tickets and answering many questions in a row is slow.
- Priority is decided from the title alone. Importing twice creates duplicate tickets.

---

## Roadmap

| Version | What it adds |
|---|---|
| **v0.1** ✅ | Ticket tracker with classes + CSV storage |
| **v0.2** ✅ | SQLite database, API import with validation, report, search, `.env` settings |
| **v1.0** ✅ | **AI sets the priority** and category, with a reason and human override |
| **v2.0** ✅ | **Answers support questions from a knowledge base**, with citations (RAG) |
| v3.0 | PostgreSQL + vector search, with measured answer quality |
| v4.0 | **AI agent auto-assigns tickets** to the right team, and escalates to a human when unsure |
| v5.0 | Web API, deployed on the cloud |
| v6.0 | Works with AI assistants through MCP |

---

## What I learned

### v2.0
- **RAG end to end, without a framework**: chunk, embed, store, retrieve, generate
- **Embeddings**: text becomes a list of numbers that represents meaning; similar meanings give similar numbers
- **Chunking**: smaller pieces match more precisely, and each chunk needs enough context (the article title) to stand alone
- **Vector databases** (Chroma): storing chunks with embeddings and metadata, and querying for the nearest ones
- Using different embedding task types for documents and for questions
- **Grounding**: making the model answer only from the retrieved text, cite its sources, and say "I don't know"
- **Evaluating RAG in two parts**: scoring retrieval and answers separately shows where a failure happened
- **Debugging the evaluation itself**: a wrong label, a duplicate article and a strict format check all looked like AI mistakes at first
- LLM answers vary between runs, so results should be checked over several runs
- Similarity scores are relative: unrelated texts still score fairly high, so ranking matters more than the absolute number
- **Tool calling**: the model asks for a function, my code checks the name and runs it, then sends the result back
- Designing functions that always return the same shape, so callers never have to guess

### v1.0
- Calling an LLM from code (Google Gemini, `google-genai`)
- Writing a **system instruction**: role, category definitions, ordered rules, priority definitions
- **Few-shot prompting** and **structured output** with Pydantic `Literal`
- **Measuring accuracy** on a labelled test set, then improving the prompt from the misses
- **Retry with backoff**, designing for failure, and keeping a **human in the loop**
- Keeping API keys in `.env`, never in code or screenshots

### v0.2
- Calling APIs with `requests`, and validating incoming data with **Pydantic**
- **SQL** with SQLite: `CREATE TABLE`, `INSERT`, `SELECT … WHERE`, `UPDATE`, `GROUP BY`, `LIKE`, `MAX`, `ALTER TABLE`
- `?` placeholders to prevent SQL injection; virtual environments, `requirements.txt` and `.env`
- Async basics: `async`/`await` and `asyncio.gather`

### v0.1
- Splitting code across files, `pathlib`, CSV with `DictReader`/`DictWriter`
- `@property` for validation, and `try/except` to handle bad input

---

Built by Preetham Patchipulusu as a learn-by-building project.