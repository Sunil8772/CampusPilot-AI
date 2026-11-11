CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('student','faculty','admin')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resources (
    id BIGSERIAL PRIMARY KEY,
    resource_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    resource_type TEXT NOT NULL CHECK (resource_type IN
      ('classroom','lab','amphitheatre','guest_house','parking')),
    location TEXT,
    capacity INTEGER NOT NULL DEFAULT 1 CHECK (capacity > 0),
    equipment TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS timetable_imports (
    id BIGSERIAL PRIMARY KEY,
    uploaded_by BIGINT REFERENCES users(id),
    program TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester > 0),
    academic_year TEXT NOT NULL,
    source_filename TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
      CHECK (status IN ('draft','published','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS timetable_versions (
    id BIGSERIAL PRIMARY KEY,
    import_id BIGINT NOT NULL REFERENCES timetable_imports(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(import_id, version_number)
);

CREATE TABLE IF NOT EXISTS timetable_entries (
    id BIGSERIAL PRIMARY KEY,
    version_id BIGINT NOT NULL REFERENCES timetable_versions(id) ON DELETE CASCADE,
    program TEXT NOT NULL,
    semester INTEGER NOT NULL,
    section TEXT,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject TEXT,
    faculty TEXT,
    room_name TEXT NOT NULL,
    course_code TEXT,
    class_type TEXT,
    batch TEXT,
    source_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (end_time > start_time)
);
CREATE INDEX IF NOT EXISTS idx_timetable_entries_lookup
  ON timetable_entries(program,semester,day_of_week,room_name);

CREATE TABLE IF NOT EXISTS room_blocks (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    reason TEXT NOT NULL,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (end_datetime > start_datetime)
);

CREATE TABLE IF NOT EXISTS bookings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    requested_capacity INTEGER NOT NULL DEFAULT 1 CHECK (requested_capacity > 0),
    purpose TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
      CHECK (status IN ('pending','approved','rejected','cancelled')),
    decision_by BIGINT REFERENCES users(id),
    decision_at TIMESTAMPTZ,
    decision_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (end_datetime > start_datetime)
);

-- Pending and approved bookings reserve the resource/time interval.
-- Half-open intervals allow adjacent bookings (e.g. 10:00-11:00, 11:00-12:00).
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_no_active_overlap;
ALTER TABLE bookings ADD CONSTRAINT bookings_no_active_overlap
  EXCLUDE USING gist (
    resource_id WITH =,
    tstzrange(start_datetime,end_datetime,'[)') WITH &&
  ) WHERE (status IN ('pending','approved'));

CREATE INDEX IF NOT EXISTS idx_bookings_user_created ON bookings(user_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bookings_status_start ON bookings(status,start_datetime);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id BIGINT REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id BIGINT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
