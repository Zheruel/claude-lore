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
upstream identity store, token issuer, federation broker, and groups source. Users sign in once at
`login.futureready.ai` — **target surface: a custom Future Ready login SPA + thin token-handler
broker in front of Cognito** (decision D1-B, §5-L); the **branded Cognito Managed Login (B2)** is the
interim surface, the enterprise-federation hand-off, and the rollback fallback. The `.futureready.ai`
session cookie gives cross-product SSO. The **LMS backend** (`fr-website-backend`) becomes an OAuth2
resource server validating Cognito tokens. The **QA platform** keeps Supabase as its session/RLS
substrate via the on-demand **`cognito-session-exchange`** edge function (no mirror Lambda — D9). A
cross-product **app switcher** (waffle) is driven by one endpoint, `GET /api/users/me/apps`. After
Phase 2 is live, **auto-tenant provisioning** removes the manual `company_fr_config` bridge and the
shared `FR_API_KEY`.

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
- ✅ `login.futureready.ai` = Cognito **Managed Login v2 — BRANDED (B2 done 2026-05-31)**, CloudFront
  `d20cuyja3hvanc.cloudfront.net`, ACTIVE; `/oauth2/authorize` → 302 → `/login`. `login-dev.futureready.ai`
  = dev equivalent (`d2ec6ah5pcam1v`, also v2-branded). Both domains flipped **v1→v2**; CloudFront + DNS
  unchanged.
- ✅ **Future Ready branding on all 6 app clients** (palette + wordmark logo + favicon + atmospheric page
  background + warm card; per §5-I). Branding ids — dev: QA `f0c90554`, Coaching `52a3c225`, Admin `3039a518`;
  prod: QA `7ccbb4a4`, Coaching `8500e799`, Admin `4857c706`. Identical surface across all three products.
  Reproducible source: `cognito-managed-login-branding/` (script + SVGs + settings + README).

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

### Redundant infra built 2026-05-31 — ✅ DECOMMISSIONED (B3, 2026-05-31)
- S3 `future-ready-login-prod`, CloudFront `E3RIXQF158R3Q8` (`dm8mfbdok3fux.cloudfront.net`), OAC
  `E2LEYS4HU0WGXE` — the standalone deploy of the shelved SPA — **all deleted, verified gone**
  (NoSuchDistribution / NoSuchOriginAccessControl / bucket 404). Was safe: dist had `Aliases:0` and DNS
  for `login.` stays on the Cognito dist `d20cuyja3hvanc`, so nothing pointed at it.

---

## 3. DECISIONS (all resolved — no open questions)

- **D1-A — (SUPERSEDED by D1-B) Login surface → brand Cognito Managed Login.** Original call:
  Managed Login + code+PKCE to ship fast with zero frontend rework; the SPA's old lib
  (`amazon-cognito-identity-js`) was deprecated. Still shipped (B2) and kept — but Managed Login's
  branding editor cannot express a bespoke design (no custom fonts / no arbitrary HTML/CSS), so it is
  now the **interim** surface, not the destination.
- **D1-B — Login surface → CUSTOM FUTURE READY SPA + token-handler broker on Cognito (DECIDED
  2026-05-31).** Build a custom SPA at `login.futureready.ai` (per `unified-login.html`) that
  authenticates against Cognito directly (SRP via **Amplify Gen2 Auth** / AWS SDK v3 — *not* the
  deprecated lib) for password users, and redirects to Cognito hosted federation for enterprise/social
  users; a thin first-party **token-handler broker** holds the Cognito refresh token httpOnly on
  `.futureready.ai` and hands products short-lived access tokens (silent SSO). Cognito stays the
  identity/token/federation/groups backend untouched — only the UI + session layer is ours.
  **Why over switching IdP (Auth0/Clerk/WorkOS):** the login problem is a *UI* problem; switching IdP
  would re-platform the whole identity layer already built (backend resource server, `lms:*`/`qa:*`
  groups, the `person_uid` spine, the QA mirror, invites, migrator, Phase F M2M), re-migrate every
  user, cost more, and complicate EU data residency — disproportionate for prettier pixels. The custom
  SPA gives full design freedom, keeps the Cognito investment, is contained to one domain, and is
  reversible (repoint to Managed Login). **Tradeoff accepted:** we now own + must secure the broker and
  every auth screen (MFA, reset, activation), and run one extra small service. Design in §5-L; runbook
  in Phase G. (Revisit IdP-switch only if frictionless per-customer enterprise SSO at scale becomes a
  core differentiator — and even then WorkOS can broker *in front of* Cognito without ripping it out.)
- **D2 — Rehearsal → DEV FOR LMS, PROD-DIRECT FOR QA.** Stage the LMS halves (backend + both LMS
  frontends + dev pool + `login-dev`) end-to-end in dev; validate; then prod. QA has **no dev env**
  (Amplify, prod-only), so QA's cutover is validated by analogy from the LMS dev run + a scoped QA
  prod test window.
- **D3 — MFA → OPTIONAL (TOTP available).** Managed Login offers TOTP enrollment at sign-in; not
  forced. Self-service post-enrollment MFA management is a deferred follow-up (§6).
- **D4 — Enterprise SAML/IdP federation → DEFERRED to a follow-up.** Ship the core Cognito cutover
  first; per-customer SAML is later Cognito config (no code change). The Managed Login surface and
  groups already support adding it without re-architecting.
- **D5 — (REVISED by D1-B) `fr-unified-login` SPA → REVIVED as the custom login surface.** The earlier
  call deleted it; D1-B brings it back. The repo was **archived, not hard-deleted** (B3), so
  `gh repo unarchive FutureReadyAS/fr-unified-login` recovers it as the design/structure starting point
  — but the **auth layer is rebuilt modern** (Amplify Gen2 Auth; drop `amazon-cognito-identity-js`). The
  throwaway standalone infra deleted in B3 stays deleted; Phase G builds proper hosting. The products'
  *own* forgot-password/activation/set-password pages still retire — those flows now move to the
  **custom SPA** (not Managed Login), and the LMS backend still deletes their endpoints at cutover; only
  the *profile* pages stay. `unified-login.html` is the SPA's design spec.
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
- ✅ **A2. Deploy `cognito-session-exchange` — DONE (2026-05-31).** Set QA Supabase identifiers
  `COGNITO_USER_POOL_ID` / `COGNITO_QA_CLIENT_ID` / `COGNITO_REGION`; added a
  `[functions.cognito-session-exchange] verify_jwt=false` block to `config.toml` (PR #289 — the
  missing block was why the GitHub integration never auto-deployed it / it 404'd); deployed via CLI
  and smoke-tested in prod: OPTIONS→200, empty body→400, garbage token→401 (our JWKS validation runs).
  Additive + inert until the QA cutover flips `VITE_AUTH_MODE=cognito`. See §5-E.
- ✅ **A3. Invite functions** rewritten + deployed (invite-agent/manager/client).
- ✅ **A4. LMS backend bridge** (`/api/users/me`, `/api/users/me/apps`) deployed, dual-auth.
- ✅ **A5. Supabase service-role key** present.

### PHASE B — Branded Managed Login (interim surface); retire the throwaway SPA infra
- ✅ **B1. D1 decided → branded Managed Login.**
- ✅ **B2. Brand Cognito Managed Login v2 — DONE (2026-05-31).** Flipped both domains v1→v2 and applied
  branding to all 6 app clients via `create/update-managed-login-branding` (Future Ready palette, wordmark
  logo, brand favicon, atmospheric deep-indigo page background + warm card; `unified-login.html` as design
  reference). Verified `login-dev.` and `login.futureready.ai` render the brand (logo + palette + composed
  dark field, indigo focus ring) and the products' OAuth2 redirect lands on it. **No frontend rework** —
  products keep code+PKCE. Accepted tradeoff: ML v2 has **no custom-font control**, so Instrument Serif rides
  on the logo only, not the "Sign in" heading. Source + rollback: `cognito-managed-login-branding/`.
- ✅ **B3. Delete the SPA — DONE (2026-05-31).** Decommissioned the redundant infra: emptied+deleted S3
  `future-ready-login-prod`, disabled→(Deployed)→deleted CloudFront `E3RIXQF158R3Q8`, deleted OAC
  `E2LEYS4HU0WGXE` (all verified gone). Repo `FutureReadyAS/fr-unified-login` **archived** (read-only,
  reversible) rather than hard-deleted — keeps history recoverable; flip to a full repo delete later if
  desired. Verified before deleting: dist had no aliases and no DNS pointed at it.

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

### PHASE G — Custom Login SPA (parallel track; per D1-B / §5-L)
Managed Login (B2) is the interim surface, so Phases C–F are **not blocked**; G swaps `login.futureready.ai`
→ the custom SPA when ready (before or after the prod cutover — a product call). Each step is reversible
(repoint `login.` to Managed Login).
- ⬜ **G1. Cognito groundwork.** Add a shared first-party web app client `futureready-web` (SRP + refresh
  for the password path; code+PKCE + an `auth.futureready.ai` callback for federation). Create the
  `auth.futureready.ai` Cognito **custom domain** (ACM us-east-1) and keep branded Managed Login there as
  the federation hand-off + fallback. Per-product clients stay during transition. (Decide single-shared
  client vs per-product — §5-L key decisions.)
- ⬜ **G2. Auth broker (BFF).** Stand up the token-handler in **eu-north-1** (API GW+Lambda / Lambda@Edge /
  co-located with an existing backend): SRP + refresh + revoke against Cognito; sets the httpOnly
  `Domain=.futureready.ai` refresh cookie; serves `/api/token` (CORS allowlist = product origins,
  credentials), `/api/logout`, and the federation `callback` code-exchange. Refresh token never reaches
  product JS.
- ⬜ **G3. Login SPA.** `gh repo unarchive` `fr-unified-login`; rebuild the auth layer on **Amplify Gen2
  Auth** (drop `amazon-cognito-identity-js`); implement every screen per `unified-login.html`: sign-in,
  MFA challenge + TOTP enroll, NEW_PASSWORD_REQUIRED (activation / force-change), forgot/reset, and the
  SSO-routing state (email-domain → "Continue to <IdP>"). Host on its own CloudFront/Amplify.
- ⬜ **G4. Product reconfig (behind existing flags).** LMS coaching+admin and QA swap the §5-C/§5-F
  "redirect to Managed Login + PKCE + store `localStorage.authToken`" for "call broker `/api/token`
  (credentials include); on 401 → redirect to the login SPA." QA then runs `cognito-session-exchange`
  →Supabase as today. LMS backend audience → the shared web client.
- ⬜ **G5. Domain swap + verify.** Disassociate the Cognito custom domain from `login.futureready.ai`;
  point `login.` DNS at the SPA's CloudFront. Verify all three products: silent SSO, password login,
  enterprise-federation redirect, MFA, reset, logout-everywhere. Rollback = repoint `login.` to Managed
  Login (re-add the Cognito custom domain on `login.`).

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

### §5-D. QA identity mirror — DONE in `cognito-session-exchange`, no Lambda (Phase A1, decision D9)
There is no mirror Lambda. The Cognito→Supabase mirror happens on-demand inside
`cognito-session-exchange`: `resolveMirroredUser` does get-by-id keyed on `custom:person_uid`
(== `auth.users.id`), and on miss `ensureRow` calls `supabaseAdmin.auth.admin.createUser({ id:
person_uid, email, email_confirm:true, user_metadata })` — `email_confirm:true` transitions
`email_confirmed_at` null→set and fires `link_user_to_agent()`, exactly as the old Supabase invite
flow. Service-role key comes from the Supabase edge-fn secret store (not AWS Secrets Manager). The
old Lambda's only extra behavior — refreshing `raw_user_meta_data` on attribute change — is not
ported (that metadata is read only at first-login routing); add to the exchange fn later if needed.

### §5-E. QA `cognito-session-exchange` (Phase A2) — written, deploy
Deploy `--no-verify-jwt` (called pre-session). Validate the Cognito **access token** via JWKS
(`createRemoteJWKSet`+`jwtVerify`): `iss`, `exp`, `token_use==="access"`, `client_id===<QA client>`.
Read `custom:person_uid` via Cognito **GetUser** (access-token-authorized; access tokens lack custom
attrs/aud). Look up `auth.users` by `person_uid`; **create on miss** (create-or-get, bounded ~3×
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

### §5-I. Branded Managed Login (Phase B2) — DONE 2026-05-31 — now the INTERIM surface + federation hand-off + fallback (destination superseded by the custom SPA, D1-B/§5-L)
Cognito Managed Login **v2** at `login.futureready.ai` (+ `login-dev`), branded per app client via
`create/update-managed-login-branding` (CLI; additive + reversible via `delete-managed-login-branding`).
Applied: Future Ready palette (cream/paper card, indigo-deep primary button → ink on hover, coral on link
hover, ink/muted text, warm-taupe input borders); the **wordmark PNG** as FORM_LOGO (centered, in-card);
brand FAVICON_SVG; an **atmospheric PAGE_BACKGROUND SVG** (deep-indigo `#1F1D2B` field + top-center radial
glow + dual concentric-ring motif + fine grain + vignette) and a warm-gradient FORM_BACKGROUND; sharp 2–4px
radii; `displayGraphics:false` (MFA/passkey screens stay on-brand, no AWS stock art); `colorSchemeMode:LIGHT`.
Reproducible source: **`cognito-managed-login-branding/`** (`build_branding.py` + the two SVGs +
`brand-settings.json` + README with clients, branding ids, re-apply, rollback). **Hard limit:** ML v2
exposes no custom web fonts — Instrument Serif/Geist cannot apply to headings, so the serif identity lives
in the logo image only. Products keep code+PKCE. No SPA, no path-routed CloudFront, no DNS cut. (Open item,
not branding: hosted pages still show a self-signup "Create an account" link — disable at the pool level if
enterprise SSO should hide it.) Under **D1-B** this is no longer the destination: once the custom SPA
(Phase G/§5-L) takes `login.`, Managed Login moves to `auth.futureready.ai` as the enterprise-federation
hand-off + rollback fallback — so the B2 work is repurposed, not wasted.

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

### §5-L. Custom Login SPA + token-handler broker (Phase G / decision D1-B)
**Shape.** `login.futureready.ai` = a custom Future Ready **SPA (UI)** + a thin first-party
**token-handler broker (BFF)**. Cognito is unchanged underneath: identity store, token issuer,
federation broker, groups source. We own only the UI + session layer.
**Auth flows.**
- *Password:* SPA → Cognito `InitiateAuth` USER_SRP_AUTH (Amplify Gen2 Auth / SDK v3) → custom screens
  for MFA / NEW_PASSWORD_REQUIRED → Cognito tokens.
- *Enterprise/social:* SPA detects the email domain → redirects to
  `auth.futureready.ai/oauth2/authorize?identity_provider=<X>&redirect_uri=<SPA callback>` → IdP auth →
  code back to the SPA → broker exchanges (PKCE) at `auth./oauth2/token`. Branded Managed Login (B2) is
  the brief on-brand surface here + the fallback.
- *Silent SSO:* broker holds the Cognito refresh token httpOnly in a `Domain=.futureready.ai` cookie.
  Product on load → `login.futureready.ai/api/token` (credentials: include) → fresh short-lived
  access/id token, or 401 → product redirects to SPA `/?return_to=<product>`.
- *Refresh / logout:* broker refreshes server-side (access tokens short-lived; refresh never in JS);
  `/api/logout` clears the cookie + Cognito `RevokeToken`/`GlobalSignOut` → single logout everywhere.
**Domain split.** SPA takes `login.futureready.ai`; Cognito hosted endpoints move to
`auth.futureready.ai` (federation hand-off + Managed Login fallback). Disassociate the Cognito custom
domain from `login.`, re-create at `auth.`; ACM `auth.` cert in us-east-1.
**Why the broker (not tokens-in-localStorage).** httpOnly refresh on `.futureready.ai` = no long-lived
token in JS (an upgrade over today's `localStorage.authToken`) + silent cross-product SSO without
Cognito's hosted cookie. The broker is the only new moving part.
**Per-service impact.** *New:* broker (eu-north-1) + login SPA (revived `fr-unified-login`, Amplify Gen2
Auth). *Changed:* the 3 frontends' token acquisition (flag-gated; §5-C/§5-F) and LMS backend audience =
the shared web client. *Unchanged:* `cognito-session-exchange`, groups, app switcher, migrator, Phase F.
**Key plan-mode decisions.** (1) Single shared `futureready-web` client — *recommended*: Cognito refresh
tokens are client-bound, so one client = one session serving all products; groups are user-bound so
authz is unaffected — vs per-product clients. (2) Broker hosting: API GW+Lambda vs Lambda@Edge vs extend
LMS backend vs Supabase edge fn (must be on `.futureready.ai`, EU region). (3) Auth lib: Amplify Gen2
Auth (wraps SRP + all challenges, maintained) vs hand-rolled SDK v3. (4) Token delivery: token-handler /
BFF (*recommended*) vs a faster-but-weaker v1 with tokens in fragment/storage.
**Sequencing & rollback.** Parallel to C–F; Managed Login stays interim so nothing is blocked; swap
`login.`→SPA when ready. Rollback: repoint `login.` to Managed Login (re-add the Cognito custom domain);
keep the web client + `auth.` domain regardless.
**Revived-SPA reality (verified 2026-05-31).** `fr-unified-login` is **~80% built**: all screens
(`SignIn`/`Mfa`/`Forgot`/`Reset`/`SelectIdp`/`Callback`), EN/NO/SV i18n, and `tokens.css` carrying the
exact `unified-login.html` palette + **real Instrument Serif/Geist** (the `--stage:#1f1d2b` field matches
the B2 Managed Login bg) — i.e. the design freedom we want, already coded. **But its cross-product SSO is
silently broken:** `cognito.ts`/`session.ts` assume that serving from `.futureready.ai` "drops the
cross-product cookie", yet `amazon-cognito-identity-js` persists to **localStorage (per-origin)** —
`login.`'s session is unreadable by `app.`/`qa.`, so each product just bounces back to login. **The §5-L
broker is exactly the fix** (and the reason a single shared client matters: Cognito refresh tokens are
client-bound, so silent cross-client SSO needs one client, not the SPA's current per-product `clientIds`
map). **G3 modernization (module-level):** swap `cognito.ts` → Amplify Gen2 Auth (keep the `AuthResult`
state machine + screens); repoint `oauth.ts` `cognitoDomain` → `auth.futureready.ai`; collapse
`config/env.ts` `clientIds`-per-product → the single web client; replace the bare
`location.assign(returnTo)` handoff (`session.ts`) with a POST to the broker (sets the httpOnly cookie)
then redirect; point `idp.ts` `VITE_IDP_LOOKUP_URL` at a broker endpoint.

---

## 6. FOLLOW-UPS (explicitly out of this initiative; future tickets)
- Enterprise SAML/IdP per-customer federation (D4) — Cognito config + `/select-idp`, no product code.
- Self-service MFA management UI (D3) — Managed Login lacks it; add to a product profile page.
- Cross-product "Also grant QA access" admin UI (D7).
- Seat-pool enforcement on auto-provisioning (D8) — only if commercial finds leakage.

## 7. ROLLBACK
- **Login surface:** if B2 ever repointed anything, DNS `login.futureready.ai` → `d20cuyja3hvanc`
  restores current Managed Login (we're staying on Cognito, so low risk).
- **Custom login SPA (Phase G):** repoint `login.futureready.ai` DNS to Managed Login / re-add the Cognito
  custom domain on `login.` → instant fallback to the branded hosted UI; the shared web client and
  `auth.futureready.ai` stay in place. Products that moved to the broker `/api/token` can flag back.
- **Frontends:** flip flags back to `jwt`/`supabase`, rebuild/redeploy.
- **Backend (D4-run):** the only hard-to-revert step — keep the revert PR staged; legacy Terraform
  stays commented, not deleted.

## 8. NEXT ACTIONS (live)
1. ~~Phase A~~ ✅ · ~~B1 decide~~ ✅ · ~~B2 brand Managed Login~~ ✅ · ~~B3 delete SPA + infra~~ ✅ — **Phases A + B done.**
2. **C** — LMS dev rehearsal (per D2): point LMS **dev** frontends at branded `login-dev`, flip dev flags
   (`VITE_AUTH_MODE=cognito`, `VITE_APP_SWITCHER_ENABLED=true`) with **dev** client ids, rebuild dev, run
   end-to-end (sign in → Coaching dev → app switcher → Admin dev; confirm dual-auth backend). _Start here._
3. Then **D** (prod window) → **E** (cleanup) → **F** (auto-provisioning).
4. **Phase G — custom login SPA** (per D1-B/§5-L) runs as a **parallel track**: it does *not* block C–F
   (Managed Login is the interim surface). Kick off whenever: G1 Cognito groundwork → G2 broker → G3 SPA →
   G4 product reconfig → G5 swap `login.`. Recommend starting G1+G2 alongside C.
- Housekeeping: **rotate the Cloudflare token** shared in the 2026-05-31 session (it's in that
  transcript).
