-- Align miked_mv_resident city/postal + metadata address with Genesys external contacts (2026-10-07).

update public.miked_mv_resident
set
  city = 'Boston',
  postal_code = '02114',
  metadata = coalesce(metadata, '{}'::jsonb) || jsonb_build_object(
    'address_line1', '150 Causeway Street',
    'state', 'MA',
    'country', 'US'
  )
where work_email = 'kimberly.green@miked.demo';

update public.miked_mv_resident
set
  city = 'Boston',
  postal_code = '02215',
  metadata = coalesce(metadata, '{}'::jsonb) || jsonb_build_object(
    'address_line1', '4 Jersey Street',
    'state', 'MA',
    'country', 'US'
  )
where work_email = 'jack.cabral@miked.demo';
