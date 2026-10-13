-- Expose registration renewal fee on profile (quote before phone/card payment).

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

  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'plate_number', r.plate_number,
        'expires_on', r.expires_on,
        'inspection_valid_through', r.inspection_valid_through,
        'status', r.status,
        'renewal_fee_dollars', round(r.renewal_fee_cents / 100.0, 2)
      )
      order by r.plate_number
    ),
    '[]'::jsonb
  ) into v_regs
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

-- Demo-friendly fees: Kimberly transcript uses $60; presenter Linus uses same for voice demos.
update public.miked_mv_vehicle_registration vr
set renewal_fee_cents = 6000
where vr.plate_number in ('LS8823', '4EF482');
