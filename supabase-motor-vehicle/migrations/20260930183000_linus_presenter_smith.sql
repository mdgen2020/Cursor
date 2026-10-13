-- Presenter persona: Linus Smith (was Turing — avoid ASR confusion on voice demos).

update public.miked_mv_resident
set last_name = 'Smith'
where work_email = 'mdgen2020@gmail.com';

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

grant execute on function public.miked_mv_resident_verify to anon, authenticated, service_role;
