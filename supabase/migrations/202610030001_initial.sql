-- Saba's server-side data store and durable Telegram inbox.
-- Apply in Supabase SQL Editor as project owner. The app connects with the
-- server-only database password; never ship it to a browser/client.

create table if not exists public.user_profiles (
    user_id text primary key,
    language text not null default 'en',
    personal_data_consent boolean not null default false,
    contact_name text,
    age text,
    birth_year text,
    location text,
    updated_at timestamptz not null default now()
);

create table if not exists public.conversation_state (
    user_id text primary key,
    stage text not null,
    updated_at timestamptz not null default now()
);

create table if not exists public.application_settings (
    key text primary key,
    value text not null,
    updated_at timestamptz not null default now()
);

create table if not exists public.audit_events (
    id bigint generated always as identity primary key,
    occurred_at timestamptz not null default now(),
    actor_id text not null,
    action text not null,
    consent boolean not null
);

create table if not exists public.vapi_calls (
    reservation_id text primary key,
    call_id text unique,
    user_id text not null,
    contact_id text not null,
    created_at timestamptz not null default now(),
    status text not null check (status in ('reserved','started','failed','completed'))
);
create index if not exists vapi_calls_daily_quota_idx on public.vapi_calls (created_at, status);

-- Durable goals following the attached task lifecycle design. User data is
-- scoped by actor_id; permissions and the current plan remain structured JSON.
create table if not exists public.goal_tasks (
    task_id uuid primary key default gen_random_uuid(),
    actor_id text not null,
    channel text not null,
    goal text not null,
    objective text not null,
    service_id text,
    status text not null default 'pending' check (status in
        ('pending','running','waiting_for_user','requires_approval','completed','failed','cancelled','paused')),
    current_step text,
    next_action text,
    subtasks jsonb not null default '[]'::jsonb,
    constraints jsonb not null default '[]'::jsonb,
    permissions jsonb not null default '{}'::jsonb,
    deadline timestamptz,
    completion_criteria text,
    created_at timestamptz not null default now(),
    last_activity timestamptz not null default now(),
    completed_at timestamptz
);
create index if not exists goal_tasks_open_by_actor_idx on public.goal_tasks (actor_id, last_activity)
    where status not in ('completed','failed','cancelled');

create table if not exists public.task_intents (
    intent_id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.goal_tasks(task_id) on delete cascade,
    action text not null,
    approved_summary_hash text not null,
    status text not null check (status in ('started','done','failed','unknown')),
    evidence jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    finished_at timestamptz
);
create index if not exists task_intents_task_status_idx on public.task_intents (task_id, status);

create table if not exists public.telegram_jobs (
    id bigint generated always as identity primary key,
    update_id bigint not null unique,
    payload jsonb not null,
    status text not null default 'queued' check (status in ('queued','processing')),
    attempts integer not null default 0,
    created_at timestamptz not null default now(),
    claimed_at timestamptz
);
create index if not exists telegram_jobs_claim_idx on public.telegram_jobs (status, created_at);

alter table public.user_profiles enable row level security;
alter table public.conversation_state enable row level security;
alter table public.application_settings enable row level security;
alter table public.audit_events enable row level security;
alter table public.vapi_calls enable row level security;
alter table public.goal_tasks enable row level security;
alter table public.task_intents enable row level security;
alter table public.telegram_jobs enable row level security;

-- No browser-facing access. The trusted backend uses its private Postgres URL.
revoke all on public.user_profiles, public.conversation_state, public.application_settings,
    public.audit_events, public.vapi_calls, public.goal_tasks, public.task_intents,
    public.telegram_jobs from anon, authenticated;
