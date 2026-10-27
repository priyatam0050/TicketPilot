# TicketPilot

An IT support ticket assistant, built from scratch in Python, one version at a time.

**End goal:** pass in a ticket's details, and AI sets the priority and auto-assigns it to the right team.

---

## Current version: v0.1

A command-line ticket tracker. Tickets are built with Python classes and stored in a CSV file, so they still exist after the program closes.

### Features

- **Create** a ticket with a title and priority (P1–P4)
- **Auto-numbering**: tickets get numbers like `INC0000001`, `INC0000002`, …
- **View** all tickets
- **Filter** tickets by priority
- **Close** a ticket (with an "already closed" check)
- **Input validation**: empty titles and invalid priorities are re-asked, never crash
- **Persistence**: tickets are saved to `ticketdetails.csv`, which is created automatically on first run

### Demo

```
Choose any of the below Option
1. Create
2. view list
3. filter by priority
4. Close
5. Quit
```

```
INC0000001 | VPN keeps disconnecting | P1 | Open
INC0000002 | Printer not working | P3 | Closed
INC0000003 | Outlook password reset | P2 | Open
```

<!-- Add a screenshot here: ![TicketPilot menu](screenshot.png) -->

---

## How to run

Requires **Python 3**. No extra packages needed.

```bash
git clone https://github.com/<your-username>/TicketPilot.git
cd TicketPilot
python3 main.py
```

---

## Project structure

```
TicketPilot/
├── main.py      # Menu: takes user input and calls TicketStore
├── models.py    # Ticket and TicketStore classes
└── .gitignore   # Keeps local data (ticketdetails.csv) out of the repo
```

### How it's designed

| Class | Responsibility |
|---|---|
| `Ticket` | One ticket: number, title, priority, status. Validates priority and knows how to `close()` itself. |
| `TicketStore` | All tickets: loads them from the CSV, saves them back, generates the next number, creates, filters and closes. |

`main.py` only talks to `TicketStore`, so the storage can change (CSV → database) without touching the menu.

---

## Roadmap

| Version | What it adds |
|---|---|
| **v0.1** ✅ | Ticket tracker with classes + CSV storage |
| v0.2 | SQLite database, data validation, importing tickets from an API |
| v1.0 | **AI sets the priority** and category from the ticket description |
| v2.0 | Answers support questions from a knowledge base, with sources (RAG) |
| v3.0 | PostgreSQL + vector search, with measured answer quality |
| v4.0 | **AI agent auto-assigns tickets** to the right team, and escalates to a human when unsure |
| v5.0 | Web API, deployed on the cloud |
| v6.0 | Works with AI assistants through MCP |

---

## What I learned in v0.1

- Splitting code across files and importing functions and classes
- `pathlib` for file paths that work on any machine
- Reading and writing CSV files with `DictReader` and `DictWriter`
- Classes, objects, `__init__`, `self`, `__str__` and `@property` for validation
- `try/except` to handle bad input without crashing
- Why a CSV row can't be edited in place: load everything, change it, write it all back

---

Built by Preetham Patchipulusu as a learn-by-building project.
