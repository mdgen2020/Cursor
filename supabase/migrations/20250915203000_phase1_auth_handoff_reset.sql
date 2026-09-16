-- Phase 1: demo auth sessions, gated RPCs, handoffs, reset
-- Provenance: demo abstraction — not production IAM
-- Requires existing EOHHS demo tables (residents, snap_*, masshealth_*) from prior setup.

-- Replace ungated RPC signatures from initial setup
drop function if exists public.dta_case_status(text);
drop function if exists public.masshealth_screening_result(text, text);

create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------------------
-- Resident ID&V fields (synthetic Linus Turing)
-- ---------------------------------------------------------------------------
alter table public.residents
  add column if not exists date_of_birth date,
  add column if not exists postal_code text;

-- ---------------------------------------------------------------------------
-- Short-lived auth sessions (authorization boundary for gated RPCs)
-- ---------------------------------------------------------------------------
create table if not exists public.demo_auth_sessions (
  id uuid primary key default gen_random_uuid(),
  session_token text not null unique,
  resident_id uuid not null references public.residents (id) on delete cascade,
  expires_at timestamptz not null default (now() + interval '2 hours'),
  created_at timestamptz not null default now()
);

create index if not exists demo_auth_sessions_token_idx
  on public.demo_auth_sessions (session_token);

alter table public.demo_auth_sessions enable row level security;

comment on table public.demo_auth_sessions is 'Demo abstraction: server-side session tokens issued after resident_verify; consumed by gated RPCs.';

-- ---------------------------------------------------------------------------
-- Escalation handoff payloads (Copilot / participant attribute assembly)
-- ---------------------------------------------------------------------------
create table if not exists public.escalation_handoffs (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.residents (id) on delete cascade,
  program text not null check (program in ('SNAP', 'MassHealth')),
  conversation_id text,
  channel text,
  summary text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists escalation_handoffs_created_at_idx
  on public.escalation_handoffs (created_at desc);

alter table public.escalation_handoffs enable row level security;

comment on table public.escalation_handoffs is 'Reasonable simulation: structured escalation packet for agent/Copilot; written before queue transfer.';

-- ---------------------------------------------------------------------------
-- Interaction events (enterprise sensor / VS narrative; Genesys tags TBD)
-- ---------------------------------------------------------------------------
create table if not exists public.interaction_events (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid references public.residents (id) on delete set null,
  program text,
  event_type text not null,
  channel text,
  conversation_id text,
  outcome text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists interaction_events_created_at_idx
  on public.interaction_events (created_at desc);

alter table public.interaction_events enable row level security;

-- ---------------------------------------------------------------------------
-- Demo reset passphrase (override via SQL in production rehearsal)
-- ---------------------------------------------------------------------------
create table if not exists public.demo_config (
  key text primary key,
  value text not null
);

insert into public.demo_config (key, value)
values ('reset_passphrase', 'eohhs-demo-reset')
on conflict (key) do nothing;

alter table public.demo_config enable row level security;

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------
create or replace function public._demo_require_reset_key(p_reset_key text)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_expected text;
begin
  select value into v_expected from public.demo_config where key = 'reset_passphrase';
  if v_expected is null or p_reset_key is distinct from v_expected then
    raise exception 'invalid reset key' using errcode = '28000';
  end if;
end;
$$;

create or replace function public._demo_resident_from_session(p_session_token text)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
begin
  if p_session_token is null or length(trim(p_session_token)) = 0 then
    raise exception 'session token required' using errcode = '28000';
  end if;

  delete from public.demo_auth_sessions where expires_at < now();

  select resident_id
  into v_resident_id
  from public.demo_auth_sessions
  where session_token = p_session_token
    and expires_at > now();

  if v_resident_id is null then
    raise exception 'invalid or expired session token' using errcode = '28000';
  end if;

  return v_resident_id;
end;
$$;

create or replace function public._demo_assert_case_access(p_case_number text, p_resident_id uuid)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_case_id uuid;
begin
  select c.id
  into v_case_id
  from public.snap_cases c
  where c.case_number = p_case_number
    and c.resident_id = p_resident_id;

  if v_case_id is null then
    raise exception 'case not found for authenticated resident' using errcode = '28000';
  end if;

  return v_case_id;
end;
$$;

-- ---------------------------------------------------------------------------
-- resident_verify — conversational ID&V (AVA Data Action)
-- ---------------------------------------------------------------------------
create or replace function public.resident_verify(
  p_first_name text,
  p_last_name text,
  p_date_of_birth date default null,
  p_case_number text default null,
  p_postal_code text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident public.residents%rowtype;
  v_token text;
  v_case_number text;
begin
  if p_first_name is null or p_last_name is null then
    raise exception 'first and last name required' using errcode = '22023';
  end if;

  select *
  into v_resident
  from public.residents r
  where lower(r.first_name) = lower(trim(p_first_name))
    and lower(r.last_name) = lower(trim(p_last_name))
    and (
      (p_date_of_birth is not null and r.date_of_birth = p_date_of_birth)
      or (
        p_case_number is not null
        and p_postal_code is not null
        and r.postal_code = trim(p_postal_code)
        and exists (
          select 1
          from public.snap_cases c
          where c.resident_id = r.id
            and c.case_number = trim(p_case_number)
        )
      )
    )
  limit 1;

  if v_resident.id is null then
    raise exception 'identity verification failed' using errcode = '28000';
  end if;

  v_token := encode(extensions.gen_random_bytes(32), 'hex');

  insert into public.demo_auth_sessions (session_token, resident_id)
  values (v_token, v_resident.id);

  select c.case_number
  into v_case_number
  from public.snap_cases c
  where c.resident_id = v_resident.id
  order by c.recert_deadline nulls last
  limit 1;

  insert into public.interaction_events (resident_id, program, event_type, metadata)
  values (
    v_resident.id,
    null,
    'resident_verified',
    jsonb_build_object('case_number', v_case_number)
  );

  return jsonb_build_object(
    'session_token', v_token,
    'resident_id', v_resident.id,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'snap_case_number', v_case_number,
    'expires_in_seconds', 7200
  );
end;
$$;

comment on function public.resident_verify is 'Demo abstraction: AVA ID&V; returns session_token for gated RPCs. Match DOB OR (case_number + postal_code).';

-- ---------------------------------------------------------------------------
-- dta_case_status — gated read (replaces single-arg version)
-- ---------------------------------------------------------------------------
create or replace function public.dta_case_status(
  p_case_number text,
  p_session_token text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_case_id uuid;
  v_result jsonb;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);
  v_case_id := public._demo_assert_case_access(p_case_number, v_resident_id);

  select jsonb_build_object(
    'resident_name', r.first_name || ' ' || r.last_name,
    'case_number', c.case_number,
    'program', c.program,
    'status', c.status,
    'recert_deadline', c.recert_deadline,
    'documents', coalesce(
      (
        select jsonb_agg(
          jsonb_build_object(
            'document_type', d.document_type,
            'status', d.status
          )
          order by d.document_type
        )
        from public.snap_case_documents d
        where d.case_id = c.id
      ),
      '[]'::jsonb
    ),
    'latest_notice', (
      select jsonb_build_object(
        'notice_type', n.notice_type,
        'sent_at', n.sent_at,
        'summary', n.summary
      )
      from public.snap_notices n
      where n.case_id = c.id
      order by n.sent_at desc
      limit 1
    )
  )
  into v_result
  from public.snap_cases c
  join public.residents r on r.id = c.resident_id
  where c.id = v_case_id;

  insert into public.interaction_events (resident_id, program, event_type, metadata)
  values (
    v_resident_id,
    'SNAP',
    'dta_case_status',
    jsonb_build_object('case_number', p_case_number)
  );

  return v_result;
end;
$$;

-- ---------------------------------------------------------------------------
-- dta_register_document — containment write
-- ---------------------------------------------------------------------------
create or replace function public.dta_register_document(
  p_case_number text,
  p_session_token text,
  p_document_type text,
  p_channel text default 'digital',
  p_conversation_id text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_case_id uuid;
  v_updated int;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);
  v_case_id := public._demo_assert_case_access(p_case_number, v_resident_id);

  update public.snap_case_documents d
  set
    status = 'received',
    received_at = now()
  where d.case_id = v_case_id
    and d.document_type = trim(p_document_type);

  get diagnostics v_updated = row_count;

  if v_updated = 0 then
    raise exception 'document type not found on case' using errcode = '22023';
  end if;

  insert into public.interaction_events (
    resident_id,
    program,
    event_type,
    channel,
    conversation_id,
    outcome,
    metadata
  )
  values (
    v_resident_id,
    'SNAP',
    'document_registered',
    p_channel,
    p_conversation_id,
    'contained',
    jsonb_build_object(
      'case_number', p_case_number,
      'document_type', p_document_type
    )
  );

  return jsonb_build_object(
    'case_number', p_case_number,
    'document_type', p_document_type,
    'status', 'received',
    'message', 'Document recorded in BEACON-shaped case file (demo simulation).'
  );
end;
$$;

-- Add received_at if missing on snap_case_documents
alter table public.snap_case_documents
  add column if not exists received_at timestamptz;

-- ---------------------------------------------------------------------------
-- MassHealth screening capture
-- ---------------------------------------------------------------------------
create or replace function public.masshealth_upsert_screening_answer(
  p_session_token text,
  p_question_key text,
  p_answer_text text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_screening_id uuid;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);

  select s.id
  into v_screening_id
  from public.masshealth_screenings s
  where s.resident_id = v_resident_id
  order by s.created_at desc nulls last
  limit 1;

  if v_screening_id is null then
    insert into public.masshealth_screenings (resident_id)
    values (v_resident_id)
    returning id into v_screening_id;
  end if;

  insert into public.masshealth_screening_answers (screening_id, question_key, answer_text)
  values (v_screening_id, trim(p_question_key), p_answer_text)
  on conflict (screening_id, question_key)
  do update set answer_text = excluded.answer_text;

  return jsonb_build_object(
    'screening_id', v_screening_id,
    'question_key', p_question_key,
    'saved', true
  );
end;
$$;

-- Ensure unique constraint for upsert (add if not exists)
do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'masshealth_screening_answers_screening_question_key'
  ) then
    alter table public.masshealth_screening_answers
      add constraint masshealth_screening_answers_screening_question_key
      unique (screening_id, question_key);
  end if;
exception
  when undefined_table then
    null;
  when undefined_column then
    null;
end;
$$;

create or replace function public.masshealth_complete_screening(
  p_session_token text,
  p_household_size int default null,
  p_income_band text default null,
  p_coverage_status text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_screening_id uuid;
  v_category text;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);

  select s.id
  into v_screening_id
  from public.masshealth_screenings s
  where s.resident_id = v_resident_id
  order by s.created_at desc nulls last
  limit 1;

  if v_screening_id is null then
    insert into public.masshealth_screenings (resident_id)
    values (v_resident_id)
    returning id into v_screening_id;
  end if;

  -- Demo abstraction: simplified rules — not an official MassHealth determination
  v_category := 'likely_eligible';

  update public.masshealth_screenings
  set
    household_size = coalesce(p_household_size, household_size),
    income_band = coalesce(p_income_band, income_band),
    coverage_status = coalesce(p_coverage_status, coverage_status),
    likely_eligibility_category = v_category,
    updated_at = now()
  where id = v_screening_id;

  insert into public.interaction_events (
    resident_id,
    program,
    event_type,
    outcome,
    metadata
  )
  values (
    v_resident_id,
    'MassHealth',
    'screening_completed',
    'screening_only',
    jsonb_build_object(
      'likely_eligibility_category', v_category,
      'disclaimer', 'Screening only — official determination by MassHealth agency.'
    )
  );

  return jsonb_build_object(
    'screening_id', v_screening_id,
    'likely_eligibility_category', v_category,
    'official_determination', false,
    'next_step', 'application'
  );
end;
$$;

create or replace function public.masshealth_screening_result(
  p_session_token text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_row public.masshealth_screenings%rowtype;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);

  select *
  into v_row
  from public.masshealth_screenings s
  where s.resident_id = v_resident_id
  order by s.created_at desc nulls last
  limit 1;

  if v_row.id is null then
    return jsonb_build_object('found', false);
  end if;

  return jsonb_build_object(
    'found', true,
    'household_size', v_row.household_size,
    'income_band', v_row.income_band,
    'coverage_status', v_row.coverage_status,
    'likely_eligibility_category', v_row.likely_eligibility_category,
    'official_determination', false
  );
end;
$$;

-- Add columns if missing on masshealth_screenings
alter table public.masshealth_screenings
  add column if not exists created_at timestamptz default now(),
  add column if not exists updated_at timestamptz;

-- ---------------------------------------------------------------------------
-- escalation_create_handoff
-- ---------------------------------------------------------------------------
create or replace function public.escalation_create_handoff(
  p_session_token text,
  p_program text,
  p_summary text,
  p_conversation_id text default null,
  p_channel text default null,
  p_payload jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_handoff_id uuid;
  v_program text;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);
  v_program := upper(trim(p_program));

  if v_program = 'MASSHEALTH' then
    v_program := 'MassHealth';
  elsif v_program = 'SNAP' then
    v_program := 'SNAP';
  else
    raise exception 'program must be SNAP or MassHealth' using errcode = '22023';
  end if;

  insert into public.escalation_handoffs (
    resident_id,
    program,
    conversation_id,
    channel,
    summary,
    payload
  )
  values (
    v_resident_id,
    v_program,
    p_conversation_id,
    p_channel,
    p_summary,
    coalesce(p_payload, '{}'::jsonb)
  )
  returning id into v_handoff_id;

  insert into public.interaction_events (
    resident_id,
    program,
    event_type,
    channel,
    conversation_id,
    outcome,
    metadata
  )
  values (
    v_resident_id,
    v_program,
    'escalation_handoff_created',
    p_channel,
    p_conversation_id,
    'escalated',
    jsonb_build_object('handoff_id', v_handoff_id)
  );

  return jsonb_build_object(
    'handoff_id', v_handoff_id,
    'program', v_program,
    'summary', p_summary,
    'payload', coalesce(p_payload, '{}'::jsonb)
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- demo_reset_scenario — presenter local script only
-- ---------------------------------------------------------------------------
create or replace function public.demo_reset_scenario(
  p_scenario text,
  p_reset_key text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_case_id uuid;
  v_scenario text;
begin
  perform public._demo_require_reset_key(p_reset_key);
  v_scenario := lower(trim(p_scenario));

  select id into v_resident_id
  from public.residents
  where lower(first_name) = 'linus' and lower(last_name) = 'turing'
  limit 1;

  select id into v_case_id
  from public.snap_cases
  where case_number = 'SNAP-MA-100234'
  limit 1;

  delete from public.demo_auth_sessions;
  delete from public.escalation_handoffs;
  delete from public.interaction_events;

  if v_case_id is not null then
    update public.snap_case_documents
    set status = 'received', received_at = now()
    where case_id = v_case_id
      and document_type in ('pay_stub', 'pay_stubs', 'proof_of_income');

    update public.snap_case_documents
    set status = 'missing', received_at = null
    where case_id = v_case_id
      and document_type in ('proof_of_rent', 'rent_proof', 'proof_of_current_rent');
  end if;

  if v_resident_id is not null and v_scenario in ('masshealth', 'masshealth_contain', 'all') then
    delete from public.masshealth_screening_answers a
    using public.masshealth_screenings s
    where a.screening_id = s.id and s.resident_id = v_resident_id;

    update public.masshealth_screenings
    set
      likely_eligibility_category = 'likely_eligible',
      updated_at = now()
    where resident_id = v_resident_id;
  end if;

  return jsonb_build_object(
    'reset', true,
    'scenario', v_scenario,
    'snap_case_number', 'SNAP-MA-100234'
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- Grants: RPCs callable via PostgREST with secret apikey (service role)
-- ---------------------------------------------------------------------------
grant execute on function public.resident_verify(text, text, date, text, text) to service_role;
grant execute on function public.dta_case_status(text, text) to service_role;
grant execute on function public.dta_register_document(text, text, text, text, text) to service_role;
grant execute on function public.masshealth_upsert_screening_answer(text, text, text) to service_role;
grant execute on function public.masshealth_complete_screening(text, integer, text, text) to service_role;
grant execute on function public.masshealth_screening_result(text) to service_role;
grant execute on function public.escalation_create_handoff(text, text, text, text, text, jsonb) to service_role;
grant execute on function public.demo_reset_scenario(text, text) to service_role;
