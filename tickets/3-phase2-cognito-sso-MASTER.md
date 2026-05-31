# Phase 2 — Cognito Federated SSO — MASTER PLAN & PROGRESS TRACKER

**Supersedes the _status/sequencing_ of `3a-lms-cognito-sso.md`, `3b-qa-cognito-sso.md`,
`3c-unified-login-and-app-switcher.md`** as the single source of truth for *where we are*
and *what's left*. Those three remain valid as detailed design docs; this file is the
live, verified state and the ordered runbook. **Update the checkboxes here as work lands** —
the whole point of this file is that we stop rediscovering state by probing prod.

> **Last verified:** 2026-05-31, by live inspection of AWS (Cognito, Lambda, CloudFront,
> ACM, S3), Supabase (functions, secrets), Cloudflare DNS, and the deployed frontend
> bundles. Every "VERIFIED" line below was checked against the live system, not assumed.

---

## 0. TL;DR — where we are

The data-plane **bridge** is live (dual-auth: both legacy and Cognito paths coexist), but
the **cutover has not happened** and **two load-bearing pieces are missing or undeployed**:

- ❌ **Mirror Lambda is still a logging stub** — the single most load-bearing piece for QA.
- ❌ **`cognito-session-exchange` is written but NOT deployed** (returns 404 in prod).
- ❌ **`login.futureready.ai` serves Cognito Managed Login, not our SPA** — and the SPA
  and product frontends use **incompatible login mechanisms** (see Decision Gate D1).

Nothing is broken in prod today: QA runs legacy Supabase password login; LMS runs legacy
home-grown JWT. All Cognito work to date is **additive and dormant**. There is no outage
risk in the current state — the risk is entirely in cutting over before the gaps are closed.

---

## 1. VERIFIED CURRENT STATE (2026-05-31)

### Cognito (AWS, eu-north-1)
- ✅ Pools: **dev** `eu-north-1_EHwfewAMC`, **prod** `eu-north-1_KPb1pLiZy`.
- ✅ App clients (OAuth `code` flow + SRP + refresh; scopes openid/email/profile; no secret;
  callback = each product's `/auth/callback`):

  | Product | DEV client id | PROD client id |
  |---|---|---|
  | QA / Conversation Intelligence | `5te70fjnnjlcg3er76eahhplh5` | `1akullaoogm2ga96motqogdbfm` |
  | Coaching / LMS end-user | `5m99osmis6vb1kebo02nt58hoh` | `359oqe65f7je5rcs7msr5t01ns` |
  | LMS admin | `317imgrhelvhoa2igsrvdlanqi` | `39q70q0258toiv55o8g9l4qflq` |

- ⚠️ **Mirror Lambda is a STUB.** `futureready-auth-mirror-{dev,prod}` — CodeSize **1103
  bytes**, LastModified **2026-04-20**, never updated. Wired as PostConfirmation +
  PostAuthentication on both pools, but the body does nothing. **The 3b step-1 work
  (write Cognito users into Supabase `auth.users`) was never shipped.**
- ✅ `login.futureready.ai` = Cognito **Managed Login v1**, CloudFront `d20cuyja3hvanc.cloudfront.net`,
  ACTIVE. `/oauth2/authorize` → 302 → `/login` (Cognito's hosted page). `login-dev.futureready.ai`
  is the dev equivalent.

### ACM (us-east-1 — required for CloudFront)
- ✅ `login.futureready.ai` cert ISSUED: `cb17c532-7723-425a-9074-ce1307041807`
- ✅ `login-dev.futureready.ai` cert ISSUED: `8e596adb-1e70-42d8-8c21-c71ffa666ee4`
- ✅ Frontend SAN cert (app/admin/api ± dev): `c9cb9c41-...` (does NOT include login)

### Cloudflare DNS (`futureready.ai`, zone `cb1a751f374c8e4a61e7673d7589e0fe`)
- `login.futureready.ai` → `d20cuyja3hvanc.cloudfront.net` (Cognito), proxied=False, ttl 300
- `login-dev.futureready.ai` → `d2ec6ah5pcam1v.cloudfront.net` (Cognito dev), proxied=False
- `qa.futureready.ai` → `d169m2igup0pjn.cloudfront.net` (Amplify; QA is **prod-only**)
- `app.futureready.ai` / `app-dev` → end-user prod/dev CloudFront
- `admin.futureready.ai` / `admin-dev` → admin prod/dev CloudFront
- `api.futureready.ai` / `api-dev` → backend prod/dev (Elastic Beanstalk via CloudFront)
- Full baseline dump saved during the 2026-05-31 session (rollback reference).

### Standalone SPA infra built this session (additive, NOT wired to any domain)
- ✅ S3 `future-ready-login-prod` (private, SSE-S3), holds the built SPA.
- ✅ CloudFront `E3RIXQF158R3Q8` → `dm8mfbdok3fux.cloudfront.net`, OAC `E2LEYS4HU0WGXE`,
  SPA error-routing, verified serving the SPA (200, deep-links, S3 locked to OAC).
- ⚠️ Built with **prod pool + prod QA/Coaching client ids**. No alias/cert attached. Not
  referenced by DNS. **Decision Gate D1 may make this redundant** — do not delete until D1
  is resolved (it cost real confusion once already).

### LMS backend (`fr-website-backend`) — dual-auth bridge LIVE
- ✅ `GET /api/users/me` → 403 unauth (deployed, prod + dev) — the Cognito-aware self endpoint.
- ✅ `GET /api/users/me/apps` → 403 unauth (deployed, prod + dev) — app-switcher source of truth.
- ✅ `POST /api/auth/login` → 400 (legacy still ALIVE, prod + dev) — home-grown JWT not yet cut.
- Net: backend accepts **both** legacy JWT and Cognito tokens right now (the additive bridge,
  PR #951–954 merged). The destructive 3a cutover (delete legacy) has NOT run.

### QA frontend (`qa-frontend`, Amplify, prod-only)
- ✅ Prod bundle contains BOTH `signInWithPassword` and `cognito-session-exchange` (the
  flag-gated cutover code is present).
- ✅ `qa.futureready.ai` returns 200 and renders (no redirect) → running in **supabase mode**
  (`VITE_AUTH_MODE` default). **QA is live on legacy password login. Not cut over. Not broken.**
- ❌ `cognito-session-exchange` edge function returns **404 — NOT DEPLOYED**. Present locally
  (`supabase/functions/cognito-session-exchange/index.ts` + `_shared/{cognito,cors,ses}.ts`).
- ✅ `invite-agent/manager/client` deployed (v22/13/13, 2026-05-11) — these are the Cognito
  rewrites (already live; new invites provision in Cognito).
- ✅ Backfill script present locally (`scripts/cognito-backfill/main.ts`), **never run**.

### Supabase edge-function secrets (QA project `odjkgcgpuhufglwgrnfj`)
- ✅ `SUPABASE_SERVICE_ROLE_KEY` **IS set** (corrects the old 3a/3b "value is empty" note).
- ✅ `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `SES_FROM_EMAIL` set (invites work).
- ❌ **Missing for the exchange fn:** `COGNITO_USER_POOL_ID`, `COGNITO_QA_CLIENT_ID`,
  `COGNITO_REGION`. Must be set before `cognito-session-exchange` can validate tokens.

### LMS frontends (Coaching `fr-end-user-adapted`, Admin `fr-adapted-admin-fe`)
- ✅ PRs merged to `development` (#729 Coaching, #649 Admin) → **dev bundles carry the Cognito
  code** (`app-dev`/`admin-dev` show `oauth2/authorize`, `cognito_pkce_verifier`).
- ❌ **Prod bundles have NO Cognito signals** — prod LMS frontends were not rebuilt from the
  merged code yet (prod deploy happens on push to `main`, which hasn't carried these).
- Env split to remember: **Coaching has dev + prod; Admin has dev + prod; QA is prod-only.**

---

## 2. DECISION GATES (must be answered before the matching phase)

### 🔴 D1 — Login architecture: SPA vs. Cognito Managed Login (BLOCKS the whole cutover)
The two halves of the project were built to **different mental models** and were never
integrated:
- **Product frontends** (QA merged; LMS PRs) do OAuth2 **authorization-code + PKCE**: they
  redirect the browser to `${COGNITO_DOMAIN}/oauth2/authorize?...redirect_uri=<product>/auth/callback`,
  Cognito mints a `code` at the product's callback, the product exchanges it at `/oauth2/token`.
  In this model the login UI is whatever Cognito serves at `/login` (today: Managed Login).
- **The `fr-unified-login` SPA** does Cognito **SDK / SRP** sign-in directly, the SDK persists
  the session, then it `location.assign(return_to)`. It never produces an authorization `code`
  for the product's `redirect_uri`, and (as coded) stores the session in the SDK's default
  localStorage — **not** a `.futureready.ai` cookie readable cross-subdomain.

These cannot both own `login.futureready.ai` as written. Pick one:

- **D1-A — Brand Cognito Managed Login (lowest risk, recommended for first cutover).**
  Keep the products' working OAuth2 code+PKCE flow. Make `login.futureready.ai` branded via
  **Cognito Managed Login v2** (logo, CSS, colors) instead of our SPA. The
  `fr-unified-login` SPA is repurposed (e.g. account/`/forgot` helpers) or shelved. No
  frontend rework. QA's partial cutover already targets this shape. **The standalone SPA
  distro built this session becomes redundant.**
- **D1-B — Make the SPA the real login surface (the original 3c vision, larger lift).**
  Rework all three product frontends from OAuth2-redirect to "redirect to the SPA at
  `login.futureready.ai/?return_to=...`; SPA signs in via SDK; drops a **CookieStorage**
  session at `.futureready.ai`; product reads it." Requires: (1) SPA `cognito.ts` switched to
  `CookieStorage({domain:'.futureready.ai'})`; (2) QA's exchange flow reworked to read the
  Cognito access token from that cookie rather than from a code exchange; (3) path-routed
  CloudFront so the SPA serves `/` while Cognito keeps `/oauth2/*` + `/.well-known/*` (for
  refresh/SAML); (4) full re-test of all three products. Higher blast radius; do not attempt
  live in one unattended session.

> **Recommendation:** D1-A for the first cutover. It's the smallest safe step, the products
> are already coded for it, and it unblocks everything else. Revisit D1-B later as an
> enhancement if the Managed Login branding proves insufficient.

### 🟠 D2 — Environments for the cutover
QA is **prod-only**; Coaching and Admin have **dev + prod**; the LMS backend has dev + prod.
Decide: **stage the entire cutover in dev first** (LMS dev frontends + dev pool + dev backend
+ a dev SPA/Managed-Login), validate end-to-end, then repeat in prod. QA has no dev, so QA's
prod cutover must be validated by analogy from the LMS dev run + a tightly-scoped prod test
window. **Recommended: yes, full dev rehearsal before any prod flip.**

### 🟠 D3 — Existing QA-only users onboarding (3b open question, still unowned)
QA-only humans (agents/managers/clients/admins never in the LMS `baseuser` table) have **no
Cognito identity**. At QA cutover they'd be locked out. The backfill script exists
(`scripts/cognito-backfill/main.ts`) but has never run. Must run (dry-run → apply) in the
window immediately before QA's flag flip, reconciled against 3a's ambiguous-email CSV.

---

## 3. PHASED RUNBOOK (ordered; check off as completed)

Legend: ✅ done · 🟡 partial/staged · ⬜ not started · 🔴 blocked on a decision gate

### PHASE A — Close the data-plane gaps (no user-visible change; mostly additive)
- ⬜ **A1. Write & deploy the mirror Lambda body** (3b step 1). Cognito
  PostConfirmation/PostAuthentication → upsert Supabase `auth.users` keyed on
  `custom:person_uid`, `email_confirm:true`. Lives in `fr-website-backend` terraform tree.
  Deploy to **dev pool first**, test with a throwaway Cognito user, then prod. _Load-bearing
  for QA; LMS does not need it._
- 🟡 **A2. Deploy `cognito-session-exchange`** (written locally, not deployed). First set the
  missing secrets: `COGNITO_USER_POOL_ID`, `COGNITO_QA_CLIENT_ID`, `COGNITO_REGION` on the QA
  Supabase project, then `supabase functions deploy cognito-session-exchange --no-verify-jwt`.
- ✅ **A3. Invite functions** already rewritten + deployed (invite-agent/manager/client).
- ✅ **A4. LMS backend bridge** (`/api/users/me`, `/api/users/me/apps`) deployed, dual-auth.
- ✅ **A5. Supabase service-role key** present.

### PHASE B — Resolve D1 and stand up the chosen login surface
- 🔴 **B1. Answer Decision Gate D1.** (Blocks B2/B3.)
- ⬜ **B2 (if D1-A).** Configure Cognito **Managed Login v2** branding on the prod pool (+ dev);
  verify `login.futureready.ai` shows the Future Ready brand; products keep OAuth2 flow.
  Decommission the standalone SPA S3+CloudFront built this session (`future-ready-login-prod`
  / `E3RIXQF158R3Q8` / OAC `E2LEYS4HU0WGXE`).
- ⬜ **B3 (if D1-B).** Rework SPA to CookieStorage + path-routed CloudFront in front of
  `login.futureready.ai` (SPA at `/`, Cognito at `/oauth2/*`); attach cert `cb17c532`; rework
  QA exchange to read the cookie; re-test. (Much larger; see D1-B.)

### PHASE C — Dev rehearsal (per Decision Gate D2)
- ⬜ **C1.** Point LMS **dev** frontends at the chosen login surface; flip dev flags
  (`VITE_AUTH_MODE=cognito`, `VITE_APP_SWITCHER_ENABLED=true`) with dev client ids.
- ⬜ **C2.** Run a dev end-to-end: log in via login surface → land in Coaching dev → app
  switcher shows accessible products → cross-navigate to Admin dev. Verify the mirror Lambda
  (A1) creates rows where applicable.
- ⬜ **C3.** Validate the LMS **dev** backend accepts Cognito tokens and legacy is still up.

### PHASE D — Prod cutover (maintenance window; the irreversible parts)
- ⬜ **D1-run. Backfill** existing QA-only users (D3): dry-run → review CSV → `--apply`.
- ⬜ **D2-run.** Build + deploy LMS **prod** frontends from `main` with cognito flags + prod
  client ids; QA prod build flip `VITE_AUTH_MODE=cognito` (+ app switcher, LMS api url).
- ⬜ **D3-run.** Verify all three products end-to-end on prod against the live login surface.
- ⬜ **D4-run. 3a destructive backend cutover** (the breaking change): flip `WebSecurityConfig`
  to OAuth2-only, delete `AuthenticationController`/`AuthenticationService`/`JwtService`/
  `JwtAuthenticationFilter` + password/activation/reset, Flyway-drop `credentials_changed_at`.
  Ship as a reviewed PR deployed **inside** the window, only after D3-run passes. Keep the
  revert PR ready.

### PHASE E — Post-cutover cleanup (only after Phase D is live & verified)
- ⬜ **E1.** Delete legacy login/activation/reset pages + routes from all three frontends and
  the Supabase-invite bridge surfaces in QA. _Blocked until prod default auth mode is cognito_
  (deleting earlier breaks login under the still-default legacy mode).
- ⬜ **E2.** Decommission redundant infra (Cognito Hosted-UI config kept commented in
  Terraform for rollback per 3a/3c; the standalone SPA distro if D1-A).
- ⬜ **E3.** Then **Phase 4** (`4-auto-tenant-provisioning.md`) is unblocked.

---

## 4. ROLLBACK
- **Login surface:** DNS for `login.futureready.ai` → revert to `d20cuyja3hvanc.cloudfront.net`
  (Cognito) restores the current Managed Login. (Only relevant if D1-B repointed it.)
- **Frontends:** flip flags back to `jwt`/`supabase`, rebuild/redeploy.
- **Backend:** the D4-run destructive PR is the only hard-to-revert step — keep its revert PR
  staged; Hosted-UI/legacy Terraform stays commented, not deleted.

## 5. OPEN ITEMS / OWNERS
- Mirror Lambda body (A1) — **unowned, load-bearing.** Biggest single gap.
- D1 architecture decision — **needs product + eng sign-off.**
- D3 QA-only backfill — script exists, **run unowned.**
- Cloudflare token used in the 2026-05-31 session is in that chat transcript — **rotate it.**
