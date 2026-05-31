# Cognito Federated SSO — MASTER TICKET & PROGRESS TRACKER

**The single source of truth for the entire Cognito SSO initiative.** Replaces and folds in
the former `3a-lms-cognito-sso.md`, `3b-qa-cognito-sso.md`, `3c-unified-login-and-app-switcher.md`,
`3c-cutover-runbook.md`, and `4-auto-tenant-provisioning.md` — all deleted. Everything you need
(state, decisions, design, ordered runbook, rollback) lives here. **Keep the checkboxes in §4
current as work lands** — the entire reason this file exists is so we stop rediscovering state
by probing prod.

> **Last verified:** 2026-05-31, by live inspection of AWS (Cognito, Lambda, CloudFront, ACM,
> S3), Supabase (functions, secrets), Cloudflare DNS, and the deployed frontend bundles. Every
> "✅ VERIFIED" line in §2 was checked against the live system, not assumed.

---

## 1. WHAT WE'RE BUILDING (one paragraph)

One identity for all Future Ready products. AWS Cognito (eu-north-1, one pool per env) is the
upstream identity broker. Users sign in once at the **branded Cognito Managed Login** at
`login.futureready.ai`; the `.futureready.ai` session cookie gives cross-product SSO. The **LMS
backend** (`fr-website-backend`) becomes an OAuth2 resource server validating Cognito tokens.
The **QA platform** keeps Supabase as its session/RLS substrate via a Cognito→Supabase **mirror
Lambda** + a **`cognito-session-exchange`** edge function. A cross-product **app switcher**
(waffle) is driven by one endpoint, `GET /api/users/me/apps`. After Phase 2 is live, **auto-tenant
provisioning** (Phase 3) removes the manual `company_fr_config` bridge and the shared `FR_API_KEY`.

Identity is keyed on **`custom:person_uid` (== Supabase `auth.users.id` == `baseuser.person_uid`),
NEVER the Cognito `sub`.** This is load-bearing — every lookup keys on `person_uid`.

---

## 2. VERIFIED CURRENT STATE (2026-05-31)

### Cognito (AWS eu-north-1)
- ✅ Pools: **dev** `eu-north-1_EHwfewAMC`, **prod** `eu-north-1_KPb1pLiZy`. Deletion protection on.
- ✅ 8 case-exact groups per pool: `lms:Administrators`, `lms:organization`, `lms:manager`,
  `lms:member`, `qa:admin`, `qa:manager`, `qa:client`, `qa:agent`.
- ✅ App clients (OAuth `code` flow + SRP + refresh; scopes openid/email/profile; no secret;
  callback = each product's `/auth/callback`):

  | Product | DEV client id | PROD client id |
  |---|---|---|
  | QA / Conversation Intelligence | `5te70fjnnjlcg3er76eahhplh5` | `1akullaoogm2ga96motqogdbfm` |
  | Coaching / LMS end-user | `5m99osmis6vb1kebo02nt58hoh` | `359oqe65f7je5rcs7msr5t01ns` |
  | LMS admin | `317imgrhelvhoa2igsrvdlanqi` | `39q70q0258toiv55o8g9l4qflq` |

- ⚠️ **Mirror Lambda — being REMOVED (decision D9).** Live `futureready-auth-mirror-{dev,prod}` is a
  1103-byte stub wired as PostConfirmation+PostAuthentication. The Terraform + Lambda source are
  removed in code (A1 done); the stub is still attached on the pools until `terraform apply` runs
  (human-reviewed). The Cognito→Supabase mirror now lives entirely in `cognito-session-exchange`.
- ✅ `login.futureready.ai` = Cognito **Managed Login v1**, CloudFront `d20cuyja3hvanc.cloudfront.net`,
  ACTIVE; `/oauth2/authorize` → 302 → `/login`. `login-dev.futureready.ai` = dev equivalent.

### ACM (us-east-1)
- ✅ `login.futureready.ai` ISSUED `cb17c532-7723-425a-9074-ce1307041807`
- ✅ `login-dev.futureready.ai` ISSUED `8e596adb-1e70-42d8-8c21-c71ffa666ee4`
- ✅ frontend SAN cert (app/admin/api ±dev) `c9cb9c41-...`

### Cloudflare DNS (`futureready.ai`, zone `cb1a751f374c8e4a61e7673d7589e0fe`)
- `login` → `d20cuyja3hvanc.cloudfront.net` (Cognito); `login-dev` → `d2ec6ah5pcam1v.cloudfront.net`
- `qa` → `d169m2igup0pjn.cloudfront.net` (**Amplify; QA is prod-only**)
- `app`/`app-dev`, `admin`/`admin-dev` → CloudFront+S3; `api`/`api-dev` → backend (EB via CloudFront)
- Full baseline dump captured 2026-05-31 (rollback reference).

### LMS backend (`fr-website-backend`) — dual-auth bridge LIVE
- ✅ `GET /api/users/me` → 403 unauth (deployed prod+dev) — Cognito-aware self endpoint.
- ✅ `GET /api/users/me/apps` → 403 unauth (deployed prod+dev) — app-switcher source of truth.
- ✅ `POST /api/auth/login` → 400 (legacy home-grown JWT **still alive**, prod+dev).
- Net: backend accepts **both** legacy JWT and Cognito tokens now (additive bridge merged). The
  destructive cutover (delete legacy) has NOT run.

### QA frontend (`qa-frontend`, Amplify, prod-only)
- ✅ Prod bundle has BOTH `signInWithPassword` and `cognito-session-exchange` (flag-gated cutover
  code present). Running in **supabase mode** (no redirect) → **live on legacy login, not cut over,
  not broken.**
- ❌ `cognito-session-exchange` edge fn → **404, NOT DEPLOYED.** Present locally
  (`supabase/functions/cognito-session-exchange/index.ts` + `_shared/{cognito,cors,ses}.ts`).
- ✅ `invite-agent/manager/client` deployed (Cognito rewrites; v22/13/13, 2026-05-11).
- ✅ Backfill script present locally (`scripts/cognito-backfill/main.ts`), **never run**.

### Supabase edge-fn secrets (QA project `odjkgcgpuhufglwgrnfj`)
- ✅ `SUPABASE_SERVICE_ROLE_KEY` IS set (corrects old "value empty" note). AWS keys + SES set.
- ❌ Missing for exchange fn: `COGNITO_USER_POOL_ID`, `COGNITO_QA_CLIENT_ID`, `COGNITO_REGION`.

### LMS frontends (Coaching `fr-end-user-adapted`, Admin `fr-adapted-admin-fe`)
- ✅ PRs merged to `development` (#729, #649) → **dev bundles carry Cognito code.**
- ❌ **Prod bundles have NO Cognito signals** — prod not rebuilt from merged code (prod deploys on
  push to `main`). Env split: **Coaching dev+prod; Admin dev+prod; QA prod-only.**

### Redundant infra built 2026-05-31 (to be torn down — see Phase B3)
- S3 `future-ready-login-prod`, CloudFront `E3RIXQF158R3Q8` (`dm8mfbdok3fux.cloudfront.net`), OAC
  `E2LEYS4HU0WGXE` — a standalone deploy of the now-shelved SPA. Decommission in B3.

---

## 3. DECISIONS (all resolved — no open questions)

- **D1 — Login surface → BRAND COGNITO MANAGED LOGIN (not a custom SPA).** AWS 2025 guidance
  favors Managed Login + auth-code+PKCE for SPAs; the SPA's lib (`amazon-cognito-identity-js`) is
  maintenance-only/deprecated; Managed Login v2 has a real branding editor (the SPA's reason to
  exist is obsolete); and all three products are *already* coded for code+PKCE → zero frontend
  rework. (Sources: AWS Security Blog "managed login vs custom UI"; Cognito Managed Login &
  branding-editor docs; PKCE-in-auth-code docs; re:Post deprecation thread.)
- **D2 — Rehearsal → DEV FOR LMS, PROD-DIRECT FOR QA.** Stage the LMS halves (backend + both LMS
  frontends + dev pool + `login-dev`) end-to-end in dev; validate; then prod. QA has **no dev env**
  (Amplify, prod-only), so QA's cutover is validated by analogy from the LMS dev run + a scoped QA
  prod test window.
- **D3 — MFA → OPTIONAL (TOTP available).** Managed Login offers TOTP enrollment at sign-in; not
  forced. Self-service post-enrollment MFA management is a deferred follow-up (§6).
- **D4 — Enterprise SAML/IdP federation → DEFERRED to a follow-up.** Ship the core Cognito cutover
  first; per-customer SAML is later Cognito config (no code change). The Managed Login surface and
  groups already support adding it without re-architecting.
- **D5 — `fr-unified-login` SPA → DELETE ENTIRELY (repo + infra).** With branded Managed Login
  owning every auth screen (sign-in, forgot/reset, activation/set-password, MFA-enroll) and the
  product apps already owning non-auth profile management, the SPA has no remaining job. ⚠ Note:
  the products' *own* forgot-password/activation/set-password pages also retire — those flows move
  to Managed Login (and the LMS backend deletes their endpoints at cutover); only the *profile*
  pages stay. The `unified-login.html` design may inform the Managed Login branding before delete.
- **D6 — Existing QA-only users → ONE-SHOT BACKFILL (Option A).** Use the existing
  `scripts/cognito-backfill/main.ts`; dry-run → apply in the QA cutover window; reconcile against
  the LMS migrator's ambiguous-email CSV so a dual-product human resolves to ONE Cognito identity.
- **D7 — Cross-product "Also grant QA access" UI (LMS admin) → DEFERRED, behind a flag.** Core
  cutover ships without it; QA invites add only `qa:*`, never `lms:*`. The LMS admin panel remains
  the only surface that grants cross-product access (added later).
- **D8 — Auto-tenant provisioning seat gating → NONE.** Unconditional auto-provision on training
  assignment (enterprise B2B contracts handle caps). Add a seat-pool check later only if commercial
  finds real leakage.
- **D9 — Mirror Lambda → DROPPED; the exchange fn is the sole mirror (DECIDED 2026-05-31).** The
  Cognito→Supabase mirror is done on-demand inside `cognito-session-exchange` (create-or-get keyed on
  `custom:person_uid`, `email_confirm:true` → fires `link_user_to_agent()`). No PostConfirmation/
  PostAuthentication Lambda. Rationale: the Lambda fired for EVERY user — including LMS-only users
  (the migrator sets `custom:person_uid` on them, so the skip-guard doesn't catch them) — doing a
  Supabase write for people who never touch Supabase, coupling LMS login to Supabase availability for
  zero benefit, and sitting in the auth hot path (a throwing PostAuthentication trigger fails the
  login). The exchange fn already does the identical create for the only users who need it (QA), at
  session-mint time. The Lambda's one extra behavior (refresh metadata on attribute change) is
  marginal — that metadata is read only at first-login routing — and can be added to the exchange fn
  later if ever needed. The full Lambda body that existed on branch `feat/auth-mirror-lambda-body`
  (merged to `development`, never applied to prod — prod ran the stub) is removed, not merged.

---

## 4. PHASED RUNBOOK (ordered; check off as completed)

Legend: ✅ done · 🟡 partial/staged · ⬜ not started

### PHASE A — Close the data-plane gaps (additive; no user-visible change)
- ✅ **A1. Mirror Lambda DROPPED (decision D9) — exchange fn is the sole mirror.** Code committed:
  removed the Lambda + its Terraform (`modules/cognito/main.tf` lambda_config/lambda/IAM/secret +
  outputs) and deleted `lambdas/auth-mirror/`; corrected `cognito-session-exchange` comments so it
  reads as the sole creator (logic already did create-or-get). ⚠ **`terraform apply` still pending**
  (human-reviewed): it detaches the triggers, destroys the Lambda+role, and schedules the now-orphan
  Supabase service-role Secrets-Manager secret for deletion (30-day recovery). Shipped as a backend
  PR + a QA PR.
- 🟡 **A2. Deploy `cognito-session-exchange`.** First set QA Supabase secrets `COGNITO_USER_POOL_ID`,
  `COGNITO_QA_CLIENT_ID`, `COGNITO_REGION`; then `supabase functions deploy cognito-session-exchange
  --no-verify-jwt`. Written locally already. See §5-E.
- ✅ **A3. Invite functions** rewritten + deployed (invite-agent/manager/client).
- ✅ **A4. LMS backend bridge** (`/api/users/me`, `/api/users/me/apps`) deployed, dual-auth.
- ✅ **A5. Supabase service-role key** present.

### PHASE B — Branded Managed Login; retire the SPA
- ✅ **B1. D1 decided → branded Managed Login.**
- ⬜ **B2. Brand Cognito Managed Login v2** on the **dev** pool, then prod (logo, palette, CSS via
  the branding editor/API; `unified-login.html` as design reference). Verify `login-dev.` then
  `login.futureready.ai` show the brand and the products' OAuth2 redirect lands on it. **No frontend
  rework** — products keep code+PKCE.
- ⬜ **B3. Delete the SPA entirely** (per D5): decommission the redundant infra built 2026-05-31
  (empty+delete S3 `future-ready-login-prod`, disable+delete CloudFront `E3RIXQF158R3Q8`, delete OAC
  `E2LEYS4HU0WGXE`), and archive/remove the `fr-unified-login` repo.

### PHASE C — LMS dev rehearsal (per D2)
- ⬜ **C1.** Point LMS **dev** frontends at branded `login-dev`; flip dev flags
  (`VITE_AUTH_MODE=cognito`, `VITE_APP_SWITCHER_ENABLED=true`) with **dev** client ids; rebuild dev.
- ⬜ **C2.** End-to-end dev run: sign in via Managed Login → land in Coaching dev → app switcher
  shows accessible products → cross-navigate to Admin dev. Confirm the mirror Lambda (A1) behaves.
- ⬜ **C3.** Confirm LMS **dev** backend accepts Cognito tokens and legacy is still up (dual-auth).

### PHASE D — Prod cutover (maintenance window; the irreversible parts)
- ⬜ **D1-run. Backfill** existing QA-only users (D6): dry-run → review ambiguous CSV → `--apply
  --confirm=yes-really-apply`. Run after the LMS migrator (PR #824).
- ⬜ **D2-run.** Build+deploy LMS **prod** frontends from `main` with cognito flags + **prod** client
  ids; flip QA prod build to `VITE_AUTH_MODE=cognito` (+ app switcher + LMS api url).
- ⬜ **D3-run.** Verify all three products end-to-end on prod against branded Managed Login.
- ⬜ **D4-run. Destructive LMS backend cutover** (breaking): flip `WebSecurityConfig` to OAuth2-only;
  delete `AuthenticationController`/`AuthenticationService`/`JwtService`/`JwtAuthenticationFilter` +
  password/activation/reset endpoints + their `MailTemplate`s; drop the `SecurityUserDetails` branch
  in `JwtAuditorAware`; Flyway-drop `baseuser.credentials_changed_at`. Reviewed PR deployed **inside**
  the window, only after D3-run passes. Keep its revert PR staged. See §5-B.

### PHASE E — Post-cutover cleanup (only after Phase D live & verified)
- ⬜ **E1.** Delete legacy auth pages/routes from all three frontends (login, activation,
  forgot/reset, QA `/set-password`) and the Supabase-invite bridge in QA. _Blocked until prod default
  auth mode is cognito_ — deleting earlier breaks login under the still-default legacy mode. Profile
  pages stay. Add 308 redirects from old `/login`,`/activate`,`/reset` → Managed Login for a grace
  window so bookmarked invite links resolve.
- ⬜ **E2.** Decommission residual infra; keep Cognito Hosted-UI/legacy Terraform **commented** (not
  deleted) for rollback.

### PHASE F — Auto-tenant provisioning (former ticket 4; starts only after Phase E)
- ⬜ **F1.** New Cognito **`qa-backend-to-lms`** app client (client-credentials/M2M). LMS integration
  endpoints (`/api/integration/*`) accept its JWT (granted `INTEGRATION` authority) **in addition to**
  the legacy `X-API-Key` during rollout; log which mechanism each call used. See §5-J.
- ⬜ **F2.** On provisioning, read the **target** user's groups via `AdminGetUser(personUid)` (not the
  service token's claims); map `lms:*` → LMS roles (case-exact strip), default `lms:member`; then
  `CognitoGroupSyncService.syncLmsGroups` writes the role back so the app switcher shows the LMS app.
  Drop the hardcoded `MEMBER_ROLE_ID=3L`. Extend the EB IAM role with `cognito-idp:AdminGetUser` +
  `AdminAddUserToGroup`.
- ⬜ **F3.** Rewrite the six QA integration edge functions (`assign-training`, `assign-team-training`,
  `confirm-team-training`, `confirm-training`, `delete-training`, `check-training-status`) to use the
  client-credentials token + `AdminGetUser` for target `person_uid`/`org_id`; drop the
  `company_fr_config` lookup; drop `FR_API_KEY`. Shared helper in `_shared/`. Kill-switch env per fn.
- ⬜ **F4.** After 2 weeks of zero legacy-path usage per customer: drop `company_fr_config` table +
  `get_company_fr_config()` RPC (rename-first holding pattern), regenerate `types/database.ts`.
- ⬜ **F5.** Remove `FR_API_KEY` + `ApiKeyAuthenticationFilter` globally (point of no return; last).

---

## 5. COMPONENT DESIGN REFERENCE (folded in from the deleted tickets)

### §5-A. Cognito infrastructure — DONE (PR #818/#819/#822)
Two pools (dev+prod), custom domains, ACM certs, 3 SPA app clients (PKCE), 8 case-exact groups,
mirror-Lambda **stub** wired as PostConfirmation+PostAuthentication, Supabase service-role secret
slot. Resource-server scaffold on the LMS classpath (`CognitoJwtAuthenticationConverter`,
`UserProvisioningService`, `CognitoGroupSyncService`, nightly `CognitoGroupReconciliationJob`) all
merged + live, no-op while `person_uid` is null (until the migrator runs). Group converter strips
`lms:` prefix **case-preserved** (`lms:Administrators` → `Administrators`); LMS accepts the **access
token** (carries `cognito:groups`), not the ID token.

### §5-B. LMS backend cutover (Phase D4-run)
`WebSecurityConfig`: replace JWT filter chain with `.oauth2ResourceServer(o→o.jwt(...))`; decode
against `cognito.issuer-uri`; validate audience = the two LMS app-client ids. `/api/auth/reload` →
`/api/users/me` (now `authenticated`, returns the same `LoginResponse` shape; note Jackson serializes
`isOrgAdmin`→`orgAdmin`). Delete `AuthenticationController`, `AuthenticationService`, `JwtService`,
`JwtAuthenticationFilter`, `MailTemplate.ACTIVATE_ACCOUNT`/`RESET_PASSWORD`, `MailService.generateToken`
call sites, `UserService.changePassword`. Drop the `SecurityUserDetails` branch from `JwtAuditorAware`.
Flyway `V109__drop_credentials_changed_at.sql` + remove `User.credentialsChangedAt`. **Do NOT** rewrite
the bulk-invite path — `BulkInviteEntryProcessor.createInvitedUser` already does the right thing.
Re-verify SSE filter ordering after the chain swap; keep `RoleChangedEvent` publish ordering.

### §5-C. LMS frontends (Phases C/D) — code merged (#729, #649)
On no Cognito session, redirect to `https://login.futureready.ai/?return_to=<enc>&product=coaching`
(end-user) — Managed Login authenticates via code+PKCE, drops the `.futureready.ai` cookie, returns;
the product reads the access token, stores it as `localStorage.authToken` (unchanged transport), calls
`/api/users/me`. Both pieces flag-gated (`VITE_AUTH_MODE`, `VITE_APP_SWITCHER_ENABLED`). Admin panel
is NOT itself a switcher app; admin switcher mounted in sidebar footer (sidebar layout has no top
chrome). `VITE_USER_SELF_PATH` (default `users/me`) lets the self/apps path be corrected to the
backend context-path (`/future-ready`) without a code change.

### §5-D. QA mirror Lambda (Phase A1) — STUB, must write
PostConfirmation/PostAuthentication → `supabaseAdmin.auth.admin` upsert of `auth.users` with
`id = custom:person_uid`, `email`, `email_confirm:true`, `user_metadata = { invited_as, agent_id,
company_id, org_id }`. `email_confirm:true` is what transitions `email_confirmed_at` null→set and
fires `link_user_to_agent()`. Idempotent re-auth refreshes metadata only. Service-role creds from
Secrets Manager. The exchange fn (§5-E) must be able to re-invoke this synchronously on a miss.

### §5-E. QA `cognito-session-exchange` (Phase A2) — written, deploy
Deploy `--no-verify-jwt` (called pre-session). Validate the Cognito **access token** via JWKS
(`createRemoteJWKSet`+`jwtVerify`): `iss`, `exp`, `token_use==="access"`, `client_id===<QA client>`.
Read `custom:person_uid` via Cognito **GetUser** (access-token-authorized; access tokens lack custom
attrs/aud). Look up `auth.users` by `person_uid`; **self-heal** on miss (re-run mirror, bounded ~3×
backoff) → else 503. Mint a Supabase session admin-side (`generateLink` magiclink →
`hashed_token` → `verifyOtp`) → return `{access_token, refresh_token}`. Env:
`COGNITO_USER_POOL_ID`, `COGNITO_QA_CLIENT_ID`, `COGNITO_REGION`.

### §5-F. QA AuthProvider cutover (Phase D2-run) — code present, flag-gated
On no Supabase session in cognito mode: redirect to Managed Login; on return,
`completeLogin(code,state)` exchanges code→Cognito tokens→`cognito-session-exchange`→
`supabase.auth.setSession`. Drop the `PASSWORD_RECOVERY` branch + `/set-password` (Cognito owns
recovery). Custom refresh adapter re-runs the Cognito refresh + re-exchange on Supabase-session
expiry.

### §5-G. QA invite rewrites — DONE (deployed)
`AdminCreateUser` (username=email, SUPPRESS, custom attrs incl. `custom:person_uid` = agent's
existing `person_uid` / random for manager-client) → `AdminAddUserToGroup` `qa:*` (never `lms:*`)
→ SES branded invite → keep the invitation-row insert. `auth.users` created later by the mirror.

### §5-H. App switcher — endpoint live; components merged
`GET /api/users/me/apps` (single source of truth) returns `{apps:[{key,name,url,availableToUser,
current}]}` from the user's groups: any `qa:*` → Conversation Intelligence; any `lms:*` (or an LMS
role) → Coaching. **Admin panel is never a switcher app.** Hide the waffle at ≤1 app. Names:
**Conversation Intelligence** (QA), **Coaching** (LMS end-user). Visual spec = `app-switcher.html`
(QA shadcn/Radix; LMS Mantine). Role→apps matrix: `qa:agent`+`lms:member`→both; `qa:*` only→CI only;
`lms:*` only→Coaching only.

### §5-I. Branded Managed Login (Phase B2) — replaces the old "SPA at login.futureready.ai"
Style the Cognito Managed Login v2 at `login.futureready.ai` (+ `login-dev`) via the branding editor:
Future Ready logo, cream/indigo/coral palette, Instrument Serif + Geist, per `unified-login.html`.
Products keep code+PKCE. No SPA, no path-routed CloudFront, no DNS cut.

### §5-J. Auto-tenant provisioning (Phase F) — former ticket 4, design intact
Every integration call is QA-service→LMS-service (caller≠target always; no self-service). Replace
shared `FR_API_KEY` with a Cognito **client-credentials** token from `qa-backend-to-lms`. LMS reads
target identity from the **request body** (`personUid`,`organizationId`,`email`,`fullName`) — the
token's `sub` is the service, not the user. Provisioning maps the **target's** `lms:*` groups (via
`AdminGetUser`) → LMS roles (case-exact), default `lms:member`, then `syncLmsGroups` writes back so
the switcher updates (≤1h token propagation, invisible since the target is offline at assign time).
Namespacing (`lms:*`/`qa:*`) is the security control — a `qa:manager` must NOT become an LMS manager.
No seat gating (D8). Drop `company_fr_config`+RPC and `FR_API_KEY`+`ApiKeyAuthenticationFilter` last,
per-customer, after 2 weeks of zero legacy-path usage.

### §5-K. Migration / backfill
- **LMS migrator** — DONE (PR #824, `@Profile("migrate")`): streams `baseuser`, backfills
  `person_uid`, `AdminCreateUser` (SUPPRESS, FORCE_CHANGE_PASSWORD), adds `lms:{role}` groups,
  ambiguous emails → CSV, optional branded SES. Double-gated dry-run. **Review+merge in lockstep
  with D4-run.**
- **QA backfill** (Phase D1-run) — `scripts/cognito-backfill/main.ts`: `AdminCreateUser` each
  existing QA user, `custom:person_uid = auth.users.id`, add `qa:<role>`; on `UsernameExists` with
  matching `person_uid` → group-merge (one identity), mismatch → CSV. Dry-run default.

---

## 6. FOLLOW-UPS (explicitly out of this initiative; future tickets)
- Enterprise SAML/IdP per-customer federation (D4) — Cognito config + `/select-idp`, no product code.
- Self-service MFA management UI (D3) — Managed Login lacks it; add to a product profile page.
- Cross-product "Also grant QA access" admin UI (D7).
- Seat-pool enforcement on auto-provisioning (D8) — only if commercial finds leakage.

## 7. ROLLBACK
- **Login surface:** if B2 ever repointed anything, DNS `login.futureready.ai` → `d20cuyja3hvanc`
  restores current Managed Login (we're staying on Cognito, so low risk).
- **Frontends:** flip flags back to `jwt`/`supabase`, rebuild/redeploy.
- **Backend (D4-run):** the only hard-to-revert step — keep the revert PR staged; legacy Terraform
  stays commented, not deleted.

## 8. NEXT ACTIONS (live)
1. **A1 mirror Lambda body** — biggest gap; everything QA depends on it. _Start here._
2. **A2** deploy exchange fn (+ 3 secrets).
3. **B2** brand Managed Login (dev→prod); **B3** delete SPA + redundant infra.
4. Then **C** (LMS dev rehearsal) → **D** (prod window) → **E** (cleanup) → **F** (auto-provisioning).
- Housekeeping: **rotate the Cloudflare token** shared in the 2026-05-31 session (it's in that
  transcript).
