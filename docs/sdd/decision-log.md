# EOHHS Demo — Decision Log

| Date | Decision |
|------|----------|
| SDD Q1 | Agent Workspace + live Copilot on escalation (Genesys-native). |
| SDD Q2 | Voice primary; identical experience on digital via same AVA/context. |
| SDD Q3 | Rent proof upload shown on digital/messaging only; voice for rest of SNAP contain path. |
| SDD Q4 | Real Virtual Supervisor on interaction screen for the interaction just completed. |
| SDD Q5 | Single EOHHS AVA front door with internal SNAP/MassHealth routing. |
| SDD Q6 | Conversational ID&V validated by Data Action against `residents`. |
| SDD Q7 | Escalations to queue **`support_miked`**. |
| SDD Q8 | No middleware BFF; AVA → Supabase RPC; digital upload via AVA; reset via local script; no Edge Functions. |
| SDD Q9 | No fallback UI; optimize reliability; abort/restart on failure. |
| SDD Q10 | Inbound voice **+1 781-277-3322** → Architect → AVA. |
