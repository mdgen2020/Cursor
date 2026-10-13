-- PostgREST cannot disambiguate overloaded miked_mv_handoff_create (PGRST203).
-- Genesys data actions send flat JSON; use p_fields_json only.

drop function if exists public.miked_mv_handoff_create(text, text, text, text, jsonb);
drop function if exists public.miked_mv_handoff_create(text, text, text, text, text);

create or replace function public.miked_mv_handoff_create(
  p_session_token text,
  p_intent_summary text,
  p_conversation_id text default null,
  p_channel text default null,
  p_fields_json text default null
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
  v_fields jsonb := '{}'::jsonb;
begin
  if p_fields_json is not null and btrim(p_fields_json) <> '' then
    v_fields := p_fields_json::jsonb;
  end if;

  v_resident_id := public.miked_mv__resident_from_session(p_session_token);
  select * into v_resident from public.miked_mv_resident where id = v_resident_id;

  insert into public.miked_mv_handoff (
    resident_id, session_token, conversation_id, channel,
    intent_summary, state_code, work_email, fields
  )
  values (
    v_resident_id, p_session_token, p_conversation_id, p_channel,
    p_intent_summary, v_resident.state_code, v_resident.work_email, v_fields
  )
  returning id into v_handoff_id;

  return jsonb_build_object(
    'handoff_id', v_handoff_id,
    'state_code', v_resident.state_code,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'work_email', v_resident.work_email,
    'intent_summary', p_intent_summary,
    'fields', v_fields
  );
end;
$$;

grant execute on function public.miked_mv_handoff_create(text, text, text, text, text) to anon, authenticated, service_role;
