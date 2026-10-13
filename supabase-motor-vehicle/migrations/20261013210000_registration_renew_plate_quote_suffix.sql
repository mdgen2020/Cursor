-- Quote renewal fee via p_plate_number suffix "|QUOTE" (no extra Hedwig input field).
-- Example: "LS8823|QUOTE" returns status quote without charging; "LS8823" processes payment.

create or replace function public.miked_mv_registration_renew(
  p_session_token text,
  p_plate_number text,
  p_quote_only boolean default false
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
  v_plate_input text;
  v_plate_compact text;
  v_quote_only boolean;
begin
  v_resident_id := public.miked_mv__resident_from_session(p_session_token);

  v_plate_input := coalesce(p_plate_number, '');
  v_quote_only := coalesce(p_quote_only, false)
    or upper(trim(v_plate_input)) like '%|QUOTE';

  v_plate_compact := upper(replace(split_part(v_plate_input, '|', 1), ' ', ''));

  select * into v_reg
  from public.miked_mv_vehicle_registration r
  where r.resident_id = v_resident_id
    and upper(replace(r.plate_number, ' ', '')) = v_plate_compact
  limit 1;

  if v_reg.id is null then
    raise exception 'registration not found' using errcode = 'P0002';
  end if;

  if v_quote_only then
    return jsonb_build_object(
      'plate_number', v_reg.plate_number,
      'amount_dollars', round(v_reg.renewal_fee_cents / 100.0, 2),
      'status', 'quote'
    );
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
