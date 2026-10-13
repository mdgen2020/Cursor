# Linus Smith — MV demo cheat sheet (print)

**AVA:** `miked_mv_front_door` · **Voice:** **+1 781-277-3322** · **Agent queue:** `support_miked` · **Script:** `miked_script_2026`

---

## Identity (ID&V)

| Field | Value |
|--------|--------|
| Legal name | **Linus Smith** |
| Date of birth | **June 23, 1988** → **`1988-06-23`** |
| State | **MA** / Massachusetts |
| Work email (Supabase + Genesys `workEmail`) | **`mdgen2020@gmail.com`** |
| Phone last-4 for verify | *(none required — leave blank unless AVA asks)* |

**If verify fails once on voice:** spell first name **L-I-N-U-S** (ASR often hears “Linux”). Last name **Smith**; ASR may accept **Smyth**.

---

## Address (Supabase + Genesys external contact)

| | |
|--|--|
| Street | **133 Franklin Street** |
| City | **Quincy** |
| State | **Massachusetts** / **MA** |
| ZIP | **02169** |

---

## RMV records (Supabase — after verify)

| | |
|--|--|
| Driver’s license # | **S50123456** |
| License expires | **December 18, 2027** (`2027-12-18`) |
| REAL ID | **No** (standard license) |
| Registration plate | **LS8823** |
| Registration expires | **October 31, 2026** (`2026-10-31`) — **renewal-ready** |
| Inspection valid through | **October 15, 2026** |
| Pre-seeded appointments | **None** — book during demo if needed |

**Say plate on voice:** **L S 8 8 2 3** (letter-by-letter, not “eighty-eight…”).  
**Renewal tool plate value:** **`LS8823`** (no spaces).

---

## Genesys (handoff / Profile)

| | |
|--|--|
| External contact GUID (Phase B handoff) | `098b33a7-9c19-42e8-b49f-6aa7f85c109c` |
| Caller ID tip | If your mobile is tied to Linus, **Profile** should match **Linus** after handoff (not another persona). |

---

## Quick demo paths (one persona)

### A — Profile lookup
1. Call **781** → ask to see **my RMV profile** / registrations.  
2. Verify: **Linus Smith**, **1988-06-23**.  
3. Expect: license **S50123456**, plate **LS8823**, reg exp **10/31/2026**.

### B — Registration renewal
1. Verify as above.  
2. Ask to **renew registration** for **LS8823** (or confirm when AVA reads the plate).  
3. Say **yes** to confirm — AVA must call renew with plate **`LS8823`**, not “yes”.

### B2 — Fee before payment (quote)
1. Verify as above.  
2. Ask **how much** renewal costs / what will be charged **before** paying (plate **L S 8 8 2 3**).  
3. Expect fee **$60** for two years (demo rate) from the system **without** a confirmation code yet.  
4. If you want to complete renewal, say **yes** — AVA renews with compact plate **`LS8823`** (no `|QUOTE` suffix).

### C — License appointment
1. Verify as above.  
2. Ask for **license renewal** or **REAL ID** appointment; pick center, date, time.  
3. AVA generates confirmation code and books via backend.

### D — Live agent (781 handoff)
1. Verify as above.  
2. Ask for a **representative** / **agent**; agree to transfer.  
3. Agent: **script** + **Profile** should show **Linus Smith**, Quincy address, ticket + license/plate/appt fields from handoff.

---

## Phrases that work well

- “I’d like to see my Massachusetts RMV profile.”  
- “I need to renew my registration — plate L S 8 8 2 3.”  
- “I want to book an appointment for license renewal.”  
- “Can I speak to someone?” / “Transfer me to an agent.”

---

## Do not use for this demo pass

Kimberly Green, Diane Martin, Jack Cabral — still in database; save for backup demos.

---

*Source: `supabase-motor-vehicle` seed + `.ava-lifecycle/miked-mv-front-door/demo-personas.md` · Updated 2026-10-13*
