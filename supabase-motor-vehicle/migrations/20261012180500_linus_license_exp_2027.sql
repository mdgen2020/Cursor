-- Linus presenter license: clearly valid through late 2027 (demo date Oct 2026).

update public.miked_mv_driver_license dl
set expires_on = date '2027-12-18', status = 'active'
from public.miked_mv_resident r
where dl.resident_id = r.id
  and r.work_email = 'mdgen2020@gmail.com';
