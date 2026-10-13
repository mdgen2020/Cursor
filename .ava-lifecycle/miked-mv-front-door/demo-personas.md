# Demo personas — `miked_mv_front_door`

Four citizens only. Each must exist as a **Genesys external contact** with `workEmail` matching Supabase **`work_email`**.

> **Default live demo:** Use **Linus Smith** only (verify, profile, **registration renewal** on plate **LS8823** due **2026-10-31**, license/appointment booking, handoff). Other personas stay seeded for later.

> **Rule:** You may edit most Supabase fields for memorable demos. If you change **`work_email`**, update the external contact **`workEmail`** in Genesys.
>
> **Handoff screen pop:** Architect loads **Genesys external contact** fields by email (`Flow.CustEmail` from AVA **`create_handoff`**). **Supabase and GC contact address/name/phone must match** what you want agents to see. See [`docs/demo/MV-handoff-script-and-profile-miked.md`](../../docs/demo/MV-handoff-script-and-profile-miked.md).

## Persona 1 — Linus Smith (presenter)

| Field | Value |
|--------|--------|
| **Role** | Default presenter / cross-demo identity |
| **DOB** | 1988-06-23 |
| **`work_email` (GC `workEmail`)** | **`mdgen2020@gmail.com`** (existing external contact) |
| **Verify** | **Linus Smith** + DOB **1988-06-23** (spell **L-I-N-U-S** if verify fails once; ASR often hears “Linux”) |
| **City** | Quincy, MA (**133 Franklin Street**, **02169** — matches GC external contact) |
| **License** | **S50123456** (standard MA, exp **2027-12-18**) |
| **Registration** | Plate **LS8823** — expires **2026-10-31** (renewal-ready; inspection through **2026-10-15**) |
| **Appointments** | Book live in AVA after verify (none pre-seeded for Linus) |
| **Voice** | AVA reads plates character-by-character (**L S 8 8 2 3**), not as one number |

## Persona 2 — Diane Martin (license renewal / REAL ID upgrade)

| Field | Value |
|--------|--------|
| **Source** | `transcripts/transcript_001_license_renewal.txt` |
| **DOB** | 1969-06-09 |
| **City** | Quincy, MA (**133 Franklin Street**, **02169** — matches GC external contact) |
| **`work_email`** | **`diane.martin@miked.demo`** |
| **Phone last-4 (verify)** | *(add in Supabase when you set external contact phone)* |
| **Demo story** | License expiring 2026-12-18; wants REAL ID; in-person appointment **MA942348492** |

Create external contact in GC with `workEmail` = `diane.martin@miked.demo`.

## Persona 3 — Kimberly Green (registration renewal)

| Field | Value |
|--------|--------|
| **Source** | `transcripts/transcript_044_registration_renewal.txt` |
| **DOB** | 1966-01-10 |
| **City** | Boston, MA (**150 Causeway Street**, **02114** — matches GC external contact) |
| **Plate** | 4EF482 |
| **Phone last-4** | 3738 |
| **`work_email`** | **`kimberly.green@miked.demo`** |
| **Demo story** | Registration renewal paid; confirmation **MA403002674** |

Create external contact with `workEmail` = `kimberly.green@miked.demo`.

## Persona 4 — Jack Cabral (REAL ID requirements)

| Field | Value |
|--------|--------|
| **Source** | `transcripts/transcript_026_real_id_requirements.txt` |
| **DOB** | 1998-04-24 |
| **Phone last-4** | 3566 |
| **`work_email`** | **`jack.cabral@miked.demo`** |
| **City** | Boston, MA (**4 Jersey Street**, **02215** — matches GC external contact) |
| **Demo story** | REAL ID document questions; optional appointment booking in transcript |

Create external contact with `workEmail` = `jack.cabral@miked.demo`.

## External contact linkage flow

1. AVA **`miked_mv_resident_verify`** → Supabase session + resident row (includes **`work_email`**).  
2. Architect / data action **search external contacts** by **`workEmail`**.  
3. Associate interaction + populate **`miked_script_2026`** MV pages (structured handoff fields).

**781 voice caveat:** The Genesys **external contact** card on the interaction often follows **caller ID (ANI)**, not AVA verify. If your mobile is linked to **Linus** (`mdgen2020@gmail.com`), you can verify **Kimberly** in AVA and still see **Linus** in the contact panel until handoff runs **`Hydrate external contact`** with **`Flow.CustEmail`** from **`create_handoff`**. For Kimberly/Diane/Jack self-service demos, create their GC external contacts and either call from a different number or accept ANI mismatch during the bot-only leg.
