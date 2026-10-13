-- Align miked_mv_resident city/postal + metadata address with Genesys external contacts (2026-10-07).

update public.miked_mv_resident
set
  city = 'Quincy',
  postal_code = '02169',
  metadata = coalesce(metadata, '{}'::jsonb) || jsonb_build_object(
    'address_line1', '133 Franklin Street',
    'state', 'MA',
    'country', 'US'
  )
where work_email = 'mdgen2020@gmail.com';

update public.miked_mv_resident
set
  city = 'Quincy',
  postal_code = '02169',
  metadata = coalesce(metadata, '{}'::jsonb) || jsonb_build_object(
    'address_line1', '133 Franklin Street',
    'state', 'MA',
    'country', 'US'
  )
where work_email = 'diane.martin@miked.demo';
