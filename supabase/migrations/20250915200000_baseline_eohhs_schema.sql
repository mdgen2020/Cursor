-- Baseline EOHHS demo schema (simulated MA programs)
-- Idempotent: safe when tables already exist on njjk (pre-Phase-1 manual setup).

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.residents (
  id uuid primary key default gen_random_uuid(),
  first_name text not null,
  last_name text not null,
  date_of_birth date,
  postal_code text,
  created_at timestamptz not null default now()
);

alter table public.residents enable row level security;

comment on table public.residents is 'Demo abstraction: synthetic residents for ID&V only; no real MA data.';

create table if not exists public.snap_cases (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.residents (id) on delete cascade,
  case_number text not null unique,
  program text not null default 'SNAP',
  status text not null default 'active',
  recert_deadline date not null,
  created_at timestamptz not null default now()
);

create index if not exists snap_cases_resident_id_idx on public.snap_cases (resident_id);
alter table public.snap_cases enable row level security;

create table if not exists public.snap_case_documents (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.snap_cases (id) on delete cascade,
  document_type text not null,
  status text not null check (status in ('received', 'pending', 'missing')),
  received_at timestamptz,
  created_at timestamptz not null default now(),
  unique (case_id, document_type)
);

create index if not exists snap_case_documents_case_id_idx on public.snap_case_documents (case_id);
alter table public.snap_case_documents enable row level security;

create table if not exists public.snap_notices (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references public.snap_cases (id) on delete cascade,
  notice_type text not null,
  sent_at timestamptz not null default now(),
  summary text not null,
  created_at timestamptz not null default now()
);

create index if not exists snap_notices_case_id_idx on public.snap_notices (case_id);
alter table public.snap_notices enable row level security;

create table if not exists public.masshealth_screenings (
  id uuid primary key default gen_random_uuid(),
  resident_id uuid not null references public.residents (id) on delete cascade,
  household_size int,
  income_band text,
  coverage_status text,
  likely_eligibility_category text,
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create index if not exists masshealth_screenings_resident_id_idx on public.masshealth_screenings (resident_id);
alter table public.masshealth_screenings enable row level security;

create table if not exists public.masshealth_screening_answers (
  id uuid primary key default gen_random_uuid(),
  screening_id uuid not null references public.masshealth_screenings (id) on delete cascade,
  question_key text not null,
  answer_text text not null,
  created_at timestamptz not null default now(),
  unique (screening_id, question_key)
);

create index if not exists masshealth_screening_answers_screening_id_idx
  on public.masshealth_screening_answers (screening_id);
alter table public.masshealth_screening_answers enable row level security;

-- Existing manual schema may omit columns added in repo migrations
alter table public.residents
  add column if not exists date_of_birth date,
  add column if not exists postal_code text;

alter table public.snap_case_documents
  add column if not exists received_at timestamptz;

alter table public.masshealth_screenings
  add column if not exists household_size int,
  add column if not exists income_band text,
  add column if not exists coverage_status text,
  add column if not exists likely_eligibility_category text,
  add column if not exists created_at timestamptz default now(),
  add column if not exists updated_at timestamptz;

alter table public.snap_notices
  add column if not exists summary text;

-- Seed only when Linus / case not present
insert into public.residents (first_name, last_name, date_of_birth, postal_code)
select 'Linus', 'Turing', date '1988-06-23', '02139'
where not exists (
  select 1 from public.residents r
  where r.first_name = 'Linus' and r.last_name = 'Turing'
);

update public.residents
set
  date_of_birth = coalesce(date_of_birth, date '1988-06-23'),
  postal_code = coalesce(postal_code, '02139')
where lower(first_name) = 'linus' and lower(last_name) = 'turing';

insert into public.snap_cases (resident_id, case_number, program, status, recert_deadline)
select r.id, 'SNAP-MA-100234', 'SNAP', 'active', (current_date + interval '21 days')::date
from public.residents r
where r.first_name = 'Linus' and r.last_name = 'Turing'
  and not exists (select 1 from public.snap_cases c where c.case_number = 'SNAP-MA-100234');

insert into public.snap_case_documents (case_id, document_type, status, received_at)
select c.id, 'pay_stub', 'received', now()
from public.snap_cases c
where c.case_number = 'SNAP-MA-100234'
  and not exists (
    select 1 from public.snap_case_documents d
    where d.case_id = c.id and d.document_type = 'pay_stub'
  );

insert into public.snap_case_documents (case_id, document_type, status)
select c.id, 'proof_of_rent', 'missing'
from public.snap_cases c
where c.case_number = 'SNAP-MA-100234'
  and not exists (
    select 1 from public.snap_case_documents d
    where d.case_id = c.id and d.document_type = 'proof_of_rent'
  );

insert into public.snap_notices (case_id, notice_type, sent_at, summary)
select
  c.id,
  'recert_reminder',
  now() - interval '3 days',
  'Your SNAP recertification is due soon. Submit any outstanding verifications to avoid an interruption in benefits.'
from public.snap_cases c
where c.case_number = 'SNAP-MA-100234'
  and not exists (
    select 1 from public.snap_notices n
    where n.case_id = c.id and n.notice_type = 'recert_reminder'
  );

insert into public.masshealth_screenings (
  resident_id, household_size, income_band, coverage_status, likely_eligibility_category
)
select r.id, 1, 'low', 'none', 'likely_eligible'
from public.residents r
where r.first_name = 'Linus' and r.last_name = 'Turing'
  and not exists (
    select 1 from public.masshealth_screenings s where s.resident_id = r.id
  );
