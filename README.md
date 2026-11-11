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
3. Copy `.env.example` to `.env`. Set `GEMINI_API_KEY` from Google AI Studio and a working PostgreSQL `DATABASE_URL`. Never commit `.env`.
4. Create an empty PostgreSQL database and ensure the database user can create the `btree_gist` extension.
5. Run `python init_db.py`.
6. Seed synthetic demo records: `python seed_demo.py`.
7. Run `streamlit run app.py`.

## Data and safety notes
- The committed master timetable contains 995 extracted rows, but every row is marked `Needs Review`. It is unverified sample input, not an authoritative live JKLU timetable.
- Source Excel/PDF timetable files are not committed. Parser scripts need source files in `data/timetables/`.
- The frontend role selector is a demo selector, not authentication. Backend functions enforce database roles, but a real login/identity provider is needed before production.
- AI parses requests and requests backend availability checks. It is not the source of truth and must not approve or confirm bookings.
- The current AI assistant can check resource availability and ask for missing details. Booking submission, authenticated user mapping, admin approval UI wiring, and full timetable upload/publish UI wiring remain to be completed.
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
