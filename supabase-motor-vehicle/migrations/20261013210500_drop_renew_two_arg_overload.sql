-- PostgREST cannot disambiguate 2-arg vs 3-arg overload; keep 3-arg function only.
drop function if exists public.miked_mv_registration_renew(text, text);
