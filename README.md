TicketPilot

An IT support ticket assistant, built from scratch in Python, one version at a time.

End goal: pass in a ticket's details, and AI sets the priority and auto-assigns it to the right team.

Current version: v0.2

Tickets are stored in a SQLite database, can be imported from an external API with validation, and can be reported on and searched.

Features: 

Create a ticket with a title and priority (P1–P4) 
Auto-numbering: tickets get numbers like INC0000001, INC0000002, …
View all tickets, in number order
Filter tickets by priority
Close a ticket (with "not found" and "already closed" checks)
Import from API: pulls sample tickets from a public API, validates each one with Pydantic, and skips bad items with a reason
Report: ticket counts by priority and by status, using SQL GROUP BY
Search: find tickets by a keyword in the title
SQLite storage: tickets are saved in ticketpilot.db, created automatically on first run
Settings in .env: API address, database name and import limit can be changed without touching code
Input validation: empty titles and invalid priorities are re-asked, never crash

Demo
Choose any of the below Option
1. Create
2. view list
3. filter by priority
4. Close
5. Import From API
6. Report
7. Search
8. Quit

INC0000001 | VPN keeps disconnecting | P1 | Open
INC0000002 | Printer not working | P3 | Closed
INC0000003 | Outlook password reset | P2 | Open
--- Tickets by priority ---
P1 : 5
P2 : 6
P3 : 5
P4 : 5
--- Tickets by Status ---
Closed : 1
Open : 20
Total Tickets : 21

How to run

Requires Python 3.

bash
# 1. Get the code
git clone https://github.com/priyatam0050/TicketPilot.git
cd TicketPilot

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the packages
pip install -r requirements.txt

# 4. Create your settings file (the defaults work as they are)
cp .env.example .env

# 5. Run
python3 main.py
Settings (.env)
Setting	What it does	Default
API_URL	Where tickets are imported from	https://jsonplaceholder.typicode.com/posts
DB_NAME	Database file name	ticketpilot.db
IMPORT_LIMIT	How many items to import	20

.env is never committed. .env.example is the template.

Project structure
TicketPilot/
├── main.py            # Menu: takes user input and calls TicketStore
├── models.py          # Ticket (one ticket) and TicketStore (SQLite storage)
├── importer.py        # Fetches posts from the API and maps them to tickets
├── schema.py          # Pydantic model (TicketIn) that validates incoming data
├── async_demo.py      # Learning demo: sequential vs async API calls
├── requirements.txt   # Packages needed to run
├── .env.example       # Template for settings
└── .gitignore         # Keeps .env, .venv and database files out of the repo

How it's designed

Part	Responsibility
Ticket	One ticket: number, title, priority, status. Validates priority and prints itself neatly.
TicketStore	The only part that touches the database: creates, views, filters, closes, reports and searches with SQL.
TicketIn	Checks outside data (from the API) before it becomes a ticket.
importer.py	Talks to the outside world and prepares data; it never stores anything itself.
main.py only talks to TicketStore, which is why moving from CSV (v0.1) to SQLite (v0.2) didn't require changing the menu.

Known limitations

Importing twice creates duplicate tickets.
Imported tickets get a placeholder priority (calculated from the post's ID). In v1.0, AI will choose the priority instead.
Roadmap

Version	What it adds
v0.1 ✅	Ticket tracker with classes + CSV storage

v0.2 ✅	SQLite database, API import with validation, report, search, .env settings

v1.0	AI sets the priority and category from the ticket description
v2.0	Answers support questions from a knowledge base, with sources (RAG)
v3.0	PostgreSQL + vector search, with measured answer quality
v4.0	AI agent auto-assigns tickets to the right team, and escalates to a human when unsure
v5.0	Web API, deployed on the cloud
v6.0	Works with AI assistants through MCP

What I learned

v0.2

Calling APIs with requests, checking status codes, and handling failures without crashing
Mapping outside data to my own format (like a transform map)
Validating incoming data with Pydantic models and field validators
SQL with SQLite: CREATE TABLE, INSERT, SELECT … WHERE, UPDATE, GROUP BY, LIKE, MAX
Always using ? placeholders to prevent SQL injection, and commit() to save changes
Virtual environments, requirements.txt, and keeping settings in .env
The difference between returning and raising an error
Async basics: async/await and asyncio.gather to run API calls at the same time

v0.1

Splitting code across files and importing functions and classes
pathlib for file paths that work on any machine
Reading and writing CSV files with DictReader and DictWriter
@property for validation, and try/except to handle bad input
Why a CSV row can't be edited in place, which SQL solved in v0.2

Built by Preetham Patchipulusu as a learn-by-building project.