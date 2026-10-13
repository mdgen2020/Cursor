-- Reset presenter registration after demo renewals (LS8823 due 2026-10-31).

update public.miked_mv_vehicle_registration vr
set
  expires_on = date '2026-10-31',
  inspection_valid_through = date '2026-10-15',
  status = 'active'
from public.miked_mv_resident r
where vr.resident_id = r.id
  and r.work_email = 'mdgen2020@gmail.com'
  and vr.plate_number = 'LS8823';
