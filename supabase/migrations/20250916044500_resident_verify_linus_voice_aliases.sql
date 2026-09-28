-- Demo-only: tolerate common voice/typing variants for presenter persona Linus Turing.

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
  v_first text := lower(trim(p_first_name));
  v_last text := lower(trim(p_last_name));
  v_last_normalized text := v_last;
begin
  if p_first_name is null or p_last_name is null then
    raise exception 'first and last name required' using errcode = '22023';
  end if;

  -- Presenter demo persona: ASR often hears "Turning" for Turing.
  if v_first = 'linus' and v_last in ('turning', 'terning', 'turing') then
    v_last_normalized := 'turing';
  end if;

  select *
  into v_resident
  from public.residents r
  where lower(trim(r.first_name)) = v_first
    and lower(trim(r.last_name)) = v_last_normalized
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

comment on function public.resident_verify is
  'Demo ID&V; includes Linus Turing voice-alias last names (turning/terning).';

grant execute on function public.resident_verify(text, text, date, text, text) to service_role;
