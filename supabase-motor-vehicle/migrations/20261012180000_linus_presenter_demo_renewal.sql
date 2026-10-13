-- Primary presenter demo: standard MA license + registration due 2026-10-31 (renewal-ready).

update public.miked_mv_driver_license dl
set
  license_number = 'S50123456',
  expires_on = date '2027-12-18',
  is_real_id = false,
  status = 'active'
from public.miked_mv_resident r
where dl.resident_id = r.id
  and r.work_email = 'mdgen2020@gmail.com';

update public.miked_mv_vehicle_registration vr
set
  expires_on = date '2026-10-31',
  inspection_valid_through = date '2026-10-15',
  status = 'active'
from public.miked_mv_resident r
where vr.resident_id = r.id
  and r.work_email = 'mdgen2020@gmail.com'
  and vr.plate_number = 'LS8823';

-- If baseline ran without the Linus plate migration, ensure one registration exists.
insert into public.miked_mv_vehicle_registration (
  resident_id, plate_number, expires_on, inspection_valid_through, status
)
select r.id, 'LS8823', date '2026-10-31', date '2026-10-15', 'active'
from public.miked_mv_resident r
where r.work_email = 'mdgen2020@gmail.com'
  and not exists (
    select 1 from public.miked_mv_vehicle_registration vr
    where vr.resident_id = r.id
  );
