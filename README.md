# CampusPilot AI — Integration Workspace

JKLU AI Buildathon PS-02 prototype: timetable-aware campus venue, guest-house and parking management.

## Integration workspace
This branch combines the Member 4 Streamlit interface, Member 1 timetable engine/data, Member 2 PostgreSQL services and Member 3 Gemini agent modules. Original member branches remain unchanged.

## Stack
- Streamlit frontend
- Gemini via the official `google-genai` SDK
- PostgreSQL via `psycopg`
- Python timetable CSV engine; parser support for Excel/PDF source files

## Local setup
1. Use Python 3.11+ and create/activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`. Set `CAMPUSPILOT_DEMO_MODE=true` only for a local synthetic-data demo, then set `GEMINI_API_KEY` from Google AI Studio and a working PostgreSQL `DATABASE_URL`. Never commit `.env`. Do not enable demo mode on a public deployment; real authentication is not included.
4. Create an empty PostgreSQL database and ensure the database user can create the `btree_gist` extension.
5. Run `python init_db.py`.
6. Seed synthetic demo records: `python seed_demo.py`.
7. Run `streamlit run app.py`.

## Data and safety notes
- The committed master timetable contains 995 extracted rows, but every row is marked `Needs Review`. It is unverified sample input, not an authoritative live JKLU timetable.
- Source Excel/PDF timetable files are not committed. Parser scripts need source files in `data/timetables/`.
- The frontend profile selector is available only when `CAMPUSPILOT_DEMO_MODE=true`. It selects fixed synthetic users and is not authentication. Do not enable this mode on a public deployment. A real login/identity provider and verified user-to-database mapping are required before production.
- AI parses requests and requests backend availability checks. PostgreSQL is the source of truth. The agent does not approve bookings; only an authorized admin action can approve a request, and the UI verifies the stored status before displaying the decision.
- The AI assistant checks resource availability and carries recent user turns only within the active clarification round. For a `book_resources` intent, the user must select a returned resource and explicitly confirm before a pending booking request is created. The Admin Panel reads pending requests from PostgreSQL, calls backend approval/rejection functions, and reads the decision back from the database. The Admin resource inventory uses PostgreSQL add/list/activate/deactivate services. The UI still uses synthetic profiles and is demo-only. Full timetable upload/parse/review/publish UI and live database-backed reports remain incomplete.
- Guest-house and parking resources are individual bookable resources. Their capacities represent room/slot capacity, not necessarily event participant capacity.
- Use synthetic/mock records only. Do not connect real student personal data or live campus systems for the buildathon demo.

## Main modules
- `availability_engine.py`: CSV timetable lookup and room conflict checks.
- `database/schema.sql`, `database/db.py`: PostgreSQL schema and connection.
- `services/`: resources, availability, bookings, RBAC, timetable versioning and audit log.
- `agent/`: Gemini extraction, orchestration and Python tool adapters.
- `app.py`: Streamlit demo UI.

## Verification required
Run locally with your own database and Gemini key. Verify database initialization, seed script, Gemini parsing, timetable data quality, all resource types, and approval conflict checks before presenting results as verified.
