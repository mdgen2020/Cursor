-- Flatten latest_notice for Genesys Data Action output (notice_type / notice_summary at root).

create or replace function public.dta_case_status(
  p_case_number text,
  p_session_token text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_resident_id uuid;
  v_case_id uuid;
  v_result jsonb;
begin
  v_resident_id := public._demo_resident_from_session(p_session_token);
  v_case_id := public._demo_assert_case_access(p_case_number, v_resident_id);

  select jsonb_build_object(
    'resident_name', r.first_name || ' ' || r.last_name,
    'case_number', c.case_number,
    'program', c.program,
    'status', c.status,
    'recert_deadline', c.recert_deadline,
    'documents', coalesce(
      (
        select jsonb_agg(
          jsonb_build_object(
            'document_type', d.document_type,
            'status', d.status
          )
          order by d.document_type
        )
        from public.snap_case_documents d
        where d.case_id = c.id
      ),
      '[]'::jsonb
    ),
    'notice_type', ln.notice_type,
    'notice_summary', ln.summary,
    'latest_notice', ln.notice_obj
  )
  into v_result
  from public.snap_cases c
  join public.residents r on r.id = c.resident_id
  left join lateral (
    select
      n.notice_type,
      n.summary,
      jsonb_build_object(
        'notice_type', n.notice_type,
        'sent_at', n.sent_at,
        'summary', n.summary
      ) as notice_obj
    from public.snap_notices n
    where n.case_id = c.id
    order by n.sent_at desc
    limit 1
  ) ln on true
  where c.id = v_case_id;

  insert into public.interaction_events (resident_id, program, event_type, metadata)
  values (
    v_resident_id,
    'SNAP',
    'dta_case_status',
    jsonb_build_object('case_number', p_case_number)
  );

  return v_result;
end;
$$;

grant execute on function public.dta_case_status(text, text) to service_role;
