# Transcript corpus analysis

**Location:** `transcripts/` (200 `.txt` files)  
**Parsed:** 2026-09-29

## Validation

| Check | Result |
|--------|--------|
| File count | **200** |
| Header `Topic:` parse | **200/200** |
| Unique citizen names | **199** (one duplicate: **Olivia Pham** ×2) |
| Topic totals vs plan | Matches planned frequency (25 / 22 / 18 for v1 slugs) |

## v1 scope (65 transcripts)

| Slug | Header topic | Count |
|------|----------------|------:|
| `license_renewal` | License Renewal | 25 |
| `registration_renewal` | Registration Renewal | 22 |
| `real_id_requirements` | REAL ID Requirements | 18 |

Remaining **135** transcripts cover phase-2+ intents (permit, suspension, title, tickets, etc.).

## File naming

`transcript_<NNN>_<slug>.txt` — slug is authoritative for batch grouping; header `Topic:` should align.

## Structure (parser contract)

- Banner + fictional disclaimer  
- Metadata block: `Call ID`, `Date`, `Topic`, `Citizen (fictional)`, `Resolution Status`, `Channel`  
- Dialogue: `Agent:` / `Citizen:` prefixed lines (may wrap)

## Demo personas (from transcripts + Linus)

See [`demo-personas.md`](demo-personas.md). Three citizens chosen from **first v1 transcript per slug** for traceability to source files:

| Persona | Source transcript | Call ID |
|---------|-------------------|---------|
| Diane Martin | `transcript_001_license_renewal.txt` | RMV-CC-2026-00001 |
| Kimberly Green | `transcript_044_registration_renewal.txt` | RMV-CC-2026-00044 |
| Jack Cabral | `transcript_026_real_id_requirements.txt` | RMV-CC-2026-00026 |
| Linus Smith | Presenter / existing GC external contact | `mdgen2020@gmail.com` |

## Next uses

- **Knowledge (SharePoint):** mine v1 + shared RMV FAQ patterns from headers and agent explanations  
- **Test scenarios:** map scenarios to persona + call ID for eval  
- **Supabase seed:** align verify fields (name, DOB, phone last-4) with transcript dialogue
