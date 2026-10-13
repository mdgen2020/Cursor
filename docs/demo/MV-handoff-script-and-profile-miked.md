# MV 781 handoff — agent script + Profile panel (`miked_script_2026`)

Goal: after AVA verify + **`create_handoff`**, the **agent** sees rich RMV context on **`miked_script_2026`** (MA RMV page **`customer_selection` = 123**) and the **left Profile** panel matches the **verified resident’s external contact** (by **`workEmail`**), not ANI-only defaults.

## Data rule (manual, your choice)

**Supabase `miked_mv_resident.work_email` must match Genesys external contact `workEmail`.**  
Address/name/city/state/zip on the **external contact** should match what you want on screen (Supabase has **city** + **postal_code**; add street lines on the GC contact — Supabase baseline does not store `address1` today).

| Persona | `work_email` | Supabase city / postal | GC contact must include |
|---------|--------------|----------------------|-------------------------|
| Linus Smith | `mdgen2020@gmail.com` | Cambridge, **02139** | MA address (not Albany NY demo junk) |
| Kimberly Green | `kimberly.green@miked.demo` | Peabody, **01960** | Same + phone last-4 **3738** |
| Diane Martin | `diane.martin@miked.demo` | Franklin, **02038** | Same |
| Jack Cabral | `jack.cabral@miked.demo` | Boston, **02108** | Phone last-4 **3566** |

After you edit contacts in **Admin → Directory → External Contacts**, re-run handoff — **Hydrate external contact** reads GC, not Supabase directly.

---

## What runs today (bot **`miked_mv_VAbotflow`** task **`MV handoff transfer`**)

1. **`Flow.CustEmail`** ← AVA **`handoff.contact_email`** when present, else **`session.contact_email`** (Supabase **`work_email`** from **`verify_resident`**) — merged in **`Resolve CustEmail from verify or handoff`** before hydrate.
2. **Data action** **`External Contact by eMail - MikeD - Full`** → **`Flow.firstname`**, **`Flow.lastname`**, address, city, state, zip.
3. **Set Screen Pop** → **`miked_script_2026`** ( **`agent_summary`** ← **`Flow.HandoffSummary`**, **`TicketNumber`** ← handoff id).
4. **Transfer to ACD** → **`Support_MikeD`**.

**Gap:** no **Set External Contact** on the **voice** interaction → Profile stays **ANI** (e.g. Linus on your mobile) even when script shows verified email.

**Gap:** script **banner** / **contact_info** / phones were mostly empty literals.

---

## Phase A — Script screen (Architect / repo YAML)

Repo canonical patch: [`archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml`](architect-exports/archy-yaml/miked_mv_VAbotflow_export_for_patch.yaml) (publish as next bot version, e.g. **v23**).

| Script input | Source (after patch) |
|--------------|----------------------|
| **`agent_summary`** | **`Flow.HandoffSummary`** |
| **`banner_text`** | **`Flow.HandoffSummary`** (headline strip on MA RMV page) |
| **`TicketNumber`** | **`Flow.TicketNumber`** |
| **`CustomerEmail`** | **`Flow.CustEmail`** |
| **`CustomerFirstName`** / **`CustomerLastName`** | Hydrate → **`Flow.firstname`** / **`Flow.lastname`** |
| Address fields | Hydrate → **`Flow.address1`**, **`Flow.city`**, **`Flow.state`**, **`Flow.zip`** |
| **`contact_info`** | **`Flow.contactPhone`** (cell/work from hydrate) |
| **`customer_name`** | **`Flow.customerDisplayName`** (first + last) |
| **`Authenticated`** | **`00AA00`** when email present (visual “verified handoff”) |
| **`customer_selection`** | **`ToString(Flow.IBVivrselection)`** (**123**) |

**Composer (MA RMV page):** Bind the **top headline** to script variable **`banner_text`** (Architect sets literal *Welcome to the Massachusetts Registry of Motor Vehicles* on handoff). Bind **ticket / reference** to **`TicketNumber`** or **`claim_number`** (6-character handoff reference from Supabase). Under the ticket, bind **driver license** → **`IncNum`**, **plate** → **`Violation1`**, **appointments (all)** → **`booking_notes`**, and optional first-appt lines → **`ApptDate`** / **`appt_date`**, **`appt_loc`**, **`appt_time`**, **`conf_numb`** (from **`create_handoff`** snapshot). Bind **`agent_summary`** to the handoff intent strip—not the main welcome line. Remove legacy copy such as *Hello, {first name}… contacting SUPPORT* or *demonstration line* from the page layout.

---

## Phase B — Left Profile panel (voice)

Goal: after verify, the **Genesys interaction Profile** (not just script fields) shows the resident tied to **`Flow.CustEmail`**, even when **ANI** is another external contact (e.g. Linus on your phone, Kimberly verified in AVA).

### Bot-flow constraint

**`Search External Contacts` / `Get External Contact` Architect actions are not allowed in `botFlow`** (Archy error: `SearchExternalContactsAction cannot be used in flows of type 'bot'`). Handoff runs inside **`miked_mv_VAbotflow`** → **`MV handoff transfer`**, so the NY DOL Messenger pattern must be adapted to **data actions only**.

### Live stack (2026-10-12)

**Approach B** — Genesys cannot expose **`contacts.id`** on **`External Contact by eMail - MikeD - Full`** via API (Archy rejects hydrate mapping; schema PUT is not supported on that wrapper action).

1. **`miked_mv_resident.genesys_external_contact_id`** + **`miked_mv_handoff_create`** returns **`genesys_external_contact_id`** (migration `20261012170000_handoff_genesys_external_contact_id.sql`).
2. **`miked_mv_front_door` 21.0 ProductionReady** — OutputData **`handoff.genesys_external_contact_id`**; handoff data action **`custom_-_65ba764d-f804-40c6-9670-c8a01fc104f7`**.
3. **`miked_mv_VAbotflow` published v29** — Call AVA maps **`handoff.genesys_external_contact_id`** → **`Flow.ContactGUID`**. In **`MV handoff transfer`**, after hydrate succeeds and before Set Screen Pop:
   - **`Get Message CommunicationID`** → **`Flow.CommID`**
   - **`Set External Contact`** (`mediaType` **`CALL`**) → **`ExternalContactID`** = **`Flow.ContactGUID`**

Snippet reference: **`miked_mv_VAbotflow_phase_b_snippet.yaml`** (update ContactGUID source to AVA output, not hydrate).

### What already works without Phase B

**Hydrate** + script bindings populate **Composer** name/address on **`miked_script_2026`** (your Diane screenshot). Phase B specifically fixes the **native Profile** card when ANI ≠ verified email.

---

## Phase C — More backend fields (optional later)

Extend **`miked_mv_handoff_create`** return JSON with **`city`**, **`postal_code`**, **`state_code`**, license snippet → new AVA **OutputData** → new **`Flow.*`** vars → extra script inputs (e.g. **`banner_text`** = summary + plate). Requires AVA publish + bot mapping; not required if GC contact + hydrate is kept in sync.

---

## Publish checklist

1. Fix **external contacts** (Phase 0 data) — Linus: **`mdgen2020@gmail.com`**.
2. **AVA 21.0+** ProductionReady with **`handoff.*`** + **`handoff.genesys_external_contact_id`**.
3. **`archy validateYaml`** → **`update`** → **`publish`** on **`miked_mv_VAbotflow_export_for_patch.yaml`** (no flow deletes).
4. Smoke **781** → **Linus Smith** → agent → script + Profile ([cheat sheet](MV-linus-smith-demo-cheat-sheet.md)).

Live org snapshot: [`architect-exports/MV-WIRING-STATUS.md`](architect-exports/MV-WIRING-STATUS.md).

Related: [`mv-script-handoff-lineage-miked.md`](mv-script-handoff-lineage-miked.md), [`MV-AVA-bot-output-mapping.md`](MV-AVA-bot-output-mapping.md).
