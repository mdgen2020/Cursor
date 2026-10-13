-- miked_mv_front_door baseline — motor_vehicle Supabase project
-- Multi-state ready; MA seed; four demo personas

create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------------------
-- Jurisdiction
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_jurisdiction (
  state_code text primary key check (char_length(state_code) = 2),
  display_name text not null,
  agency_name text not null,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

insert into public.miked_mv_jurisdiction (state_code, display_name, agency_name)
values ('MA', 'Massachusetts', 'Massachusetts RMV')
on conflict (state_code) do nothing;

-- ---------------------------------------------------------------------------
-- Residents (demo personas; work_email joins to Genesys external contact)
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_resident (
  id uuid primary key default gen_random_uuid(),
  state_code text not null references public.miked_mv_jurisdiction (state_code),
  first_name text not null,
  last_name text not null,
  date_of_birth date not null,
  work_email text not null,
  phone_last4 text,
  city text,
  postal_code text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (state_code, work_email)
);

create index if not exists miked_mv_resident_name_dob_idx
  on public.miked_mv_resident (state_code, lower(first_name), lower(last_name), date_of_birth);

alter table public.miked_mv_resident enable row level security;

-- ---------------------------------------------------------------------------
-- Auth sessions
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_auth_session (
  id uuid primary key default gen_random_uuid(),
  session_token text not null unique,
  resident_id uuid not null references public.miked_mv_resident (id) on delete cascade,
  conversation_id text,
  channel text,
  expires_at timestamptz not null default (now() + interval '2 hours'),
  created_at timestamptz not null default now()
);

create index if not exists miked_mv_auth_session_token_idx
  on public.miked_mv_auth_session (session_token);

alter table public.miked_mv_auth_session enable row level security;

-- ---------------------------------------------------------------------------
-- Driver license (v1: renewal + REAL ID)
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_driver_license (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.miked_mv_resident (id) on delete cascade,
  license_number text not null,
  class text not null default 'D',
  expires_on date not null,
  is_real_id boolean not null default false,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  unique (resident_id)
);

alter table public.miked_mv_driver_license enable row level security;

-- ---------------------------------------------------------------------------
-- Vehicle registration (v1: renewal)
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_vehicle_registration (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.miked_mv_resident (id) on delete cascade,
  plate_number text not null,
  expires_on date not null,
  inspection_valid_through date,
  renewal_fee_cents integer not null default 4300,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  unique (plate_number)
);

create index if not exists miked_mv_vehicle_registration_resident_idx
  on public.miked_mv_vehicle_registration (resident_id);

alter table public.miked_mv_vehicle_registration enable row level security;

-- ---------------------------------------------------------------------------
-- Appointments (RMV service center)
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_appointment (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.miked_mv_resident (id) on delete cascade,
  confirmation_code text not null unique,
  service_center text not null,
  scheduled_at timestamptz not null,
  purpose text not null,
  status text not null default 'scheduled',
  created_at timestamptz not null default now()
);

alter table public.miked_mv_appointment enable row level security;

-- ---------------------------------------------------------------------------
-- Registration renewal transactions
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_registration_renewal (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.miked_mv_resident (id) on delete cascade,
  registration_id uuid not null references public.miked_mv_vehicle_registration (id) on delete cascade,
  confirmation_code text not null unique,
  amount_cents integer not null,
  paid_at timestamptz not null default now()
);

alter table public.miked_mv_registration_renewal enable row level security;

-- ---------------------------------------------------------------------------
-- Escalation handoffs (structured script fields)
-- ---------------------------------------------------------------------------
create table if not exists public.miked_mv_handoff (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid references public.miked_mv_resident (id) on delete set null,
  session_token text,
  conversation_id text,
  channel text,
  intent_summary text not null,
  state_code text,
  work_email text,
  fields jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.miked_mv_handoff enable row level security;

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv__resident_from_session(p_session_token text)
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
  select s.resident_id into v_resident_id
  from public.miked_mv_auth_session s
  where s.session_token = p_session_token
    and s.expires_at > now();
  if v_resident_id is null then
    raise exception 'invalid or expired session' using errcode = '28000';
  end if;
  return v_resident_id;
end;
$$;

-- ---------------------------------------------------------------------------
-- RPC: resident verify (voice-friendly name match)
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv_resident_verify(
  p_state_code text,
  p_first_name text,
  p_last_name text,
  p_date_of_birth date,
  p_phone_last4 text default null,
  p_conversation_id text default null,
  p_channel text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_first text := lower(trim(p_first_name));
  v_last text := lower(trim(p_last_name));
  v_resident public.miked_mv_resident%rowtype;
  v_token text;
begin
  if p_state_code is null or length(trim(p_state_code)) <> 2 then
    raise exception 'state_code required' using errcode = '22023';
  end if;

  select * into v_resident
  from public.miked_mv_resident r
  where r.state_code = upper(trim(p_state_code))
    and lower(r.first_name) = v_first
    and lower(r.last_name) = v_last
    and r.date_of_birth = p_date_of_birth
  limit 1;

  if v_resident.id is null then
    raise exception 'resident not found' using errcode = 'P0002';
  end if;

  if p_phone_last4 is not null and length(trim(p_phone_last4)) > 0 then
    if v_resident.phone_last4 is distinct from trim(p_phone_last4) then
      raise exception 'phone verification failed' using errcode = '28000';
    end if;
  end if;

  v_token := encode(extensions.gen_random_bytes(24), 'hex');

  insert into public.miked_mv_auth_session (session_token, resident_id, conversation_id, channel)
  values (v_token, v_resident.id, p_conversation_id, p_channel);

  return jsonb_build_object(
    'session_token', v_token,
    'expires_in_seconds', 7200,
    'state_code', v_resident.state_code,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'work_email', v_resident.work_email
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- RPC: profile for session (license + registrations)
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv_get_profile(p_session_token text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_license jsonb;
  v_regs jsonb;
  v_resident public.miked_mv_resident%rowtype;
begin
  v_resident_id := public.miked_mv__resident_from_session(p_session_token);
  select * into v_resident from public.miked_mv_resident where id = v_resident_id;

  select to_jsonb(l) - 'id' - 'resident_id' - 'created_at' into v_license
  from public.miked_mv_driver_license l
  where l.resident_id = v_resident_id;

  select coalesce(jsonb_agg(to_jsonb(r) - 'id' - 'resident_id' - 'created_at'), '[]'::jsonb) into v_regs
  from public.miked_mv_vehicle_registration r
  where r.resident_id = v_resident_id;

  return jsonb_build_object(
    'state_code', v_resident.state_code,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'work_email', v_resident.work_email,
    'city', v_resident.city,
    'driver_license', coalesce(v_license, 'null'::jsonb),
    'registrations', v_regs
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- RPC: registration renewal (v1 self-service)
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv_registration_renew(
  p_session_token text,
  p_plate_number text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_reg public.miked_mv_vehicle_registration%rowtype;
  v_conf text;
begin
  v_resident_id := public.miked_mv__resident_from_session(p_session_token);

  select * into v_reg
  from public.miked_mv_vehicle_registration r
  where r.resident_id = v_resident_id
    and upper(replace(r.plate_number, ' ', '')) = upper(replace(p_plate_number, ' ', ''))
  limit 1;

  if v_reg.id is null then
    raise exception 'registration not found' using errcode = 'P0002';
  end if;

  v_conf := 'MA' || lpad((floor(random() * 999999999)::bigint)::text, 9, '0');

  update public.miked_mv_vehicle_registration
  set expires_on = expires_on + interval '2 years',
      status = 'active'
  where id = v_reg.id;

  insert into public.miked_mv_registration_renewal (resident_id, registration_id, confirmation_code, amount_cents)
  values (v_resident_id, v_reg.id, v_conf, v_reg.renewal_fee_cents);

  return jsonb_build_object(
    'confirmation_code', v_conf,
    'plate_number', v_reg.plate_number,
    'new_expires_on', (select expires_on from public.miked_mv_vehicle_registration where id = v_reg.id),
    'amount_dollars', round(v_reg.renewal_fee_cents / 100.0, 2),
    'status', 'paid'
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- RPC: book license service appointment (REAL ID / renewal in person)
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv_license_book_appointment(
  p_session_token text,
  p_purpose text,
  p_service_center text,
  p_scheduled_at timestamptz,
  p_confirmation_code text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
begin
  v_resident_id := public.miked_mv__resident_from_session(p_session_token);

  if p_confirmation_code is null or length(trim(p_confirmation_code)) < 6 then
    raise exception 'confirmation_code required' using errcode = '22023';
  end if;

  insert into public.miked_mv_appointment (resident_id, confirmation_code, service_center, scheduled_at, purpose)
  values (v_resident_id, trim(p_confirmation_code), p_service_center, p_scheduled_at, p_purpose);

  return jsonb_build_object(
    'confirmation_code', trim(p_confirmation_code),
    'service_center', p_service_center,
    'scheduled_at', p_scheduled_at,
    'purpose', p_purpose,
    'status', 'scheduled'
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- RPC: escalation handoff packet
-- ---------------------------------------------------------------------------
create or replace function public.miked_mv_handoff_create(
  p_session_token text,
  p_intent_summary text,
  p_conversation_id text default null,
  p_channel text default null,
  p_fields jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_resident public.miked_mv_resident%rowtype;
  v_handoff_id uuid;
begin
  v_resident_id := public.miked_mv__resident_from_session(p_session_token);
  select * into v_resident from public.miked_mv_resident where id = v_resident_id;

  insert into public.miked_mv_handoff (
    resident_id, session_token, conversation_id, channel,
    intent_summary, state_code, work_email, fields
  )
  values (
    v_resident_id, p_session_token, p_conversation_id, p_channel,
    p_intent_summary, v_resident.state_code, v_resident.work_email, coalesce(p_fields, '{}'::jsonb)
  )
  returning id into v_handoff_id;

  return jsonb_build_object(
    'handoff_id', v_handoff_id,
    'state_code', v_resident.state_code,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'work_email', v_resident.work_email,
    'intent_summary', p_intent_summary,
    'fields', coalesce(p_fields, '{}'::jsonb)
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- MA seed — four personas
-- ---------------------------------------------------------------------------
insert into public.miked_mv_resident (
  state_code, first_name, last_name, date_of_birth, work_email, phone_last4, city, postal_code
)
select 'MA', 'Linus', 'Smith', date '1988-06-23', 'mdgen2020@gmail.com', null, 'Cambridge', '02139'
where not exists (select 1 from public.miked_mv_resident where work_email = 'mdgen2020@gmail.com');

insert into public.miked_mv_resident (
  state_code, first_name, last_name, date_of_birth, work_email, phone_last4, city, postal_code
)
select 'MA', 'Diane', 'Martin', date '1969-06-09', 'diane.martin@miked.demo', null, 'Franklin', '02038'
where not exists (select 1 from public.miked_mv_resident where work_email = 'diane.martin@miked.demo');

insert into public.miked_mv_resident (
  state_code, first_name, last_name, date_of_birth, work_email, phone_last4, city, postal_code
)
select 'MA', 'Kimberly', 'Green', date '1966-01-10', 'kimberly.green@miked.demo', '3738', 'Peabody', '01960'
where not exists (select 1 from public.miked_mv_resident where work_email = 'kimberly.green@miked.demo');

insert into public.miked_mv_resident (
  state_code, first_name, last_name, date_of_birth, work_email, phone_last4, city, postal_code
)
select 'MA', 'Jack', 'Cabral', date '1998-04-24', 'jack.cabral@miked.demo', '3566', 'Boston', '02108'
where not exists (select 1 from public.miked_mv_resident where work_email = 'jack.cabral@miked.demo');

-- Licenses
insert into public.miked_mv_driver_license (resident_id, license_number, expires_on, is_real_id)
select r.id, 'S99988801', date '2026-12-18', false
from public.miked_mv_resident r where r.work_email = 'diane.martin@miked.demo'
  and not exists (select 1 from public.miked_mv_driver_license dl where dl.resident_id = r.id);

insert into public.miked_mv_driver_license (resident_id, license_number, expires_on, is_real_id)
select r.id, 'S12345678', date '2027-03-15', false
from public.miked_mv_resident r where r.work_email = 'kimberly.green@miked.demo'
  and not exists (select 1 from public.miked_mv_driver_license dl where dl.resident_id = r.id);

insert into public.miked_mv_driver_license (resident_id, license_number, expires_on, is_real_id)
select r.id, 'S11223344', date '2027-08-01', false
from public.miked_mv_resident r where r.work_email = 'jack.cabral@miked.demo'
  and not exists (select 1 from public.miked_mv_driver_license dl where dl.resident_id = r.id);

insert into public.miked_mv_driver_license (resident_id, license_number, expires_on, is_real_id)
select r.id, 'S00000001', date '2027-01-01', true
from public.miked_mv_resident r where r.work_email = 'mdgen2020@gmail.com'
  and not exists (select 1 from public.miked_mv_driver_license dl where dl.resident_id = r.id);

-- Registrations
insert into public.miked_mv_vehicle_registration (resident_id, plate_number, expires_on, inspection_valid_through)
select r.id, '4EF482', date '2026-12-08', date '2026-11-01'
from public.miked_mv_resident r where r.work_email = 'kimberly.green@miked.demo'
  and not exists (select 1 from public.miked_mv_vehicle_registration vr where vr.plate_number = '4EF482');

insert into public.miked_mv_vehicle_registration (resident_id, plate_number, expires_on, inspection_valid_through)
select r.id, 'JK3075', date '2026-12-06', date '2026-10-15'
from public.miked_mv_resident r where r.work_email = 'diane.martin@miked.demo'
  and not exists (select 1 from public.miked_mv_vehicle_registration vr where vr.plate_number = 'JK3075');

-- Diane transcript appointment (optional replay)
insert into public.miked_mv_appointment (resident_id, confirmation_code, service_center, scheduled_at, purpose)
select r.id, 'MA942348492', 'Boston RMV Service Center', timestamptz '2026-09-21 10:00:00-04', 'REAL ID license renewal'
from public.miked_mv_resident r where r.work_email = 'diane.martin@miked.demo'
  and not exists (select 1 from public.miked_mv_appointment a where a.confirmation_code = 'MA942348492');

grant usage on schema public to anon, authenticated, service_role;
grant execute on function public.miked_mv_resident_verify to anon, authenticated, service_role;
grant execute on function public.miked_mv_get_profile to anon, authenticated, service_role;
grant execute on function public.miked_mv_registration_renew to anon, authenticated, service_role;
grant execute on function public.miked_mv_license_book_appointment to anon, authenticated, service_role;
grant execute on function public.miked_mv_handoff_create to anon, authenticated, service_role;
