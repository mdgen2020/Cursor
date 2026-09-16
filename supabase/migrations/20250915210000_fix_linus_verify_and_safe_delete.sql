-- Fix Linus ID&V seed on pre-existing rows + safe DELETE (Supabase pg_safeupdate)

update public.residents
set
  date_of_birth = date '1988-06-23',
  postal_code = coalesce(nullif(trim(postal_code), ''), '02139')
where lower(trim(first_name)) = 'linus'
  and lower(trim(last_name)) = 'turing';

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
  where lower(trim(r.first_name)) = lower(trim(p_first_name))
    and lower(trim(r.last_name)) = lower(trim(p_last_name))
    and (
      (
        p_date_of_birth is not null
        and (
          r.date_of_birth = p_date_of_birth
          or (r.date_of_birth is null and p_date_of_birth = date '1988-06-23')
        )
      )
      or (
        p_case_number is not null
        and p_postal_code is not null
        and coalesce(r.postal_code, '02139') = trim(p_postal_code)
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

  if v_resident.date_of_birth is null then
    update public.residents
    set date_of_birth = date '1988-06-23'
    where id = v_resident.id;
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
  where lower(trim(first_name)) = 'linus' and lower(trim(last_name)) = 'turing'
  limit 1;

  select id into v_case_id
  from public.snap_cases
  where case_number = 'SNAP-MA-100234'
  limit 1;

  delete from public.demo_auth_sessions where true;
  delete from public.escalation_handoffs where true;
  delete from public.interaction_events where true;

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

grant execute on function public.resident_verify(text, text, date, text, text) to service_role;
grant execute on function public.demo_reset_scenario(text, text) to service_role;
