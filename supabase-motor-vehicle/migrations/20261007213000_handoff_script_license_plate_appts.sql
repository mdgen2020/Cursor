-- Enrich handoff_create for agent script: license #, plate(s), scheduled appointments.

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
  v_reference_code text;
  v_fields jsonb := '{}'::jsonb;
  v_license_number text;
  v_plate_number text;
  v_appointments_summary text;
  v_appointment_date text;
  v_appointment_location text;
  v_appointment_time text;
  v_appointment_confirmation text;
begin
  if p_fields_json is not null and btrim(p_fields_json) <> '' then
    v_fields := p_fields_json::jsonb;
  end if;

  v_resident_id := public.miked_mv__resident_from_session(p_session_token);
  select * into v_resident from public.miked_mv_resident where id = v_resident_id;

  select dl.license_number into v_license_number
  from public.miked_mv_driver_license dl
  where dl.resident_id = v_resident_id;

  select coalesce(string_agg(r.plate_number, ', ' order by r.plate_number), '')
  into v_plate_number
  from public.miked_mv_vehicle_registration r
  where r.resident_id = v_resident_id;

  select coalesce(
    string_agg(
      trim(purpose) || ' — ' || trim(service_center) || ' on '
        || to_char(scheduled_at at time zone 'America/New_York', 'Mon DD, YYYY at HH12:MI AM')
        || ' (conf ' || confirmation_code || ')',
      '; '
      order by scheduled_at
    ),
    ''
  )
  into v_appointments_summary
  from public.miked_mv_appointment a
  where a.resident_id = v_resident_id
    and a.status = 'scheduled'
    and a.scheduled_at >= (now() - interval '2 hours');

  select
    a.confirmation_code,
    a.service_center,
    to_char(a.scheduled_at at time zone 'America/New_York', 'YYYY-MM-DD'),
    to_char(a.scheduled_at at time zone 'America/New_York', 'HH12:MI AM')
  into
    v_appointment_confirmation,
    v_appointment_location,
    v_appointment_date,
    v_appointment_time
  from public.miked_mv_appointment a
  where a.resident_id = v_resident_id
    and a.status = 'scheduled'
    and a.scheduled_at >= (now() - interval '2 hours')
  order by a.scheduled_at asc
  limit 1;

  loop
    v_reference_code := public.miked_mv__handoff_reference_code();
    exit when not exists (
      select 1 from public.miked_mv_handoff h where h.reference_code = v_reference_code
    );
  end loop;

  v_fields := v_fields || jsonb_build_object(
    'license_number', coalesce(v_license_number, ''),
    'plate_number', coalesce(v_plate_number, ''),
    'appointments_summary', coalesce(v_appointments_summary, '')
  );

  insert into public.miked_mv_handoff (
    resident_id, session_token, conversation_id, channel,
    intent_summary, state_code, work_email, fields, reference_code
  )
  values (
    v_resident_id, p_session_token, p_conversation_id, p_channel,
    p_intent_summary, v_resident.state_code, v_resident.work_email, v_fields, v_reference_code
  )
  returning id into v_handoff_id;

  return jsonb_build_object(
    'handoff_id', v_reference_code,
    'handoff_uuid', v_handoff_id,
    'state_code', v_resident.state_code,
    'resident_name', v_resident.first_name || ' ' || v_resident.last_name,
    'work_email', v_resident.work_email,
    'intent_summary', p_intent_summary,
    'license_number', coalesce(v_license_number, ''),
    'plate_number', coalesce(v_plate_number, ''),
    'appointments_summary', coalesce(v_appointments_summary, ''),
    'appointment_date', coalesce(v_appointment_date, ''),
    'appointment_location', coalesce(v_appointment_location, ''),
    'appointment_time', coalesce(v_appointment_time, ''),
    'appointment_confirmation', coalesce(v_appointment_confirmation, ''),
    'fields', v_fields
  );
end;
$$;

grant execute on function public.miked_mv_handoff_create(text, text, text, text, text) to anon, authenticated, service_role;
