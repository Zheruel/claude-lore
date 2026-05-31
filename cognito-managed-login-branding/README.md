# Cognito Managed Login v2 — Future Ready branding (Ticket B2)

Reproducible source for the branded Cognito **Managed Login v2** at `login.futureready.ai`
and `login-dev.futureready.ai`. Applied 2026-05-31 (master ticket §4 B2 / §5-I).

Design reference: `../unified-login.html`. Faithful within Managed Login v2's limits — see
**Known limitation** below.

## What was applied

- Both pool domains flipped **ManagedLoginVersion 1 → 2** (CloudFront + DNS unchanged).
- A branding style created on **all 6 app clients** (3 dev + 3 prod) so the login surface is
  identical regardless of which product starts the OAuth flow.
- Palette (from `unified-login.html`): deep-indigo atmospheric page field, warm cream/paper
  card, indigo-deep primary button (cream text, ink on hover), coral accent on link hover,
  ink/muted text, warm-taupe input borders, sharp 2–4px radii.
- Assets: **FORM_LOGO** = Future Ready wordmark PNG (`fr-end-user-adapted/public/images/logo.png`,
  centered, in-card); **FAVICON_SVG** = `fr-unified-login/public/favicon.svg`;
  **PAGE_BACKGROUND** = `fr-page-background.svg` (indigo `#1F1D2B` + top-center radial glow +
  dual concentric-ring motif + fine grain + vignette); **FORM_BACKGROUND** = `fr-form-background.svg`
  (warm paper gradient + faint coral ring flourish + micro-grain).
- `displayGraphics:false` (MFA/passkey screens stay on-brand, no AWS stock illustrations);
  `colorSchemeMode:LIGHT`.

## Known limitation (accepted tradeoff of D1-A)

Managed Login v2 exposes **no custom web-font control**. Instrument Serif / Geist cannot be
applied to the headings, so the serif identity lives in the **logo image only** — the "Sign in"
heading renders in Cognito's stock sans. This is inherent to choosing Managed Login over the
shelved custom SPA.

## Pools, clients, branding ids

| Pool | env | QA client / brandingId | Coaching client / brandingId | Admin client / brandingId |
|---|---|---|---|---|
| `eu-north-1_EHwfewAMC` | dev  | `5te70fjnnjlcg3er76eahhplh5` / `f0c90554` | `5m99osmis6vb1kebo02nt58hoh` / `52a3c225` | `317imgrhelvhoa2igsrvdlanqi` / `3039a518` |
| `eu-north-1_KPb1pLiZy` | prod | `1akullaoogm2ga96motqogdbfm` / `7ccbb4a4` | `359oqe65f7je5rcs7msr5t01ns` / `8500e799` | `39q70q0258toiv55o8g9l4qflq` / `4857c706` |

## Re-apply / regenerate

`build_branding.py` deep-merges the brand overrides onto Cognito's **default** settings
document, then base64-embeds the three assets and writes `brand-settings.json` + the assets list.
It expects the Cognito default as a base at `/tmp/ml_merged.json`; regenerate that first:

```bash
# 1. seed the default settings document (any client works as the template)
aws cognito-idp create-managed-login-branding --region eu-north-1 \
  --user-pool-id eu-north-1_EHwfewAMC --client-id <clientId> \
  --use-cognito-provided-values --query 'ManagedLoginBranding.ManagedLoginBrandingId' --output text
aws cognito-idp describe-managed-login-branding --region eu-north-1 \
  --user-pool-id eu-north-1_EHwfewAMC --managed-login-branding-id <id> \
  --return-merged-resources > /tmp/ml_merged.json   # wrap: {"ManagedLoginBranding": {...}}

# 2. build the payload
python3 build_branding.py            # -> brand-settings.json + (in-memory) assets list

# 3. apply to a client (create if new, update if it exists)
aws cognito-idp update-managed-login-branding --region eu-north-1 \
  --cli-input-json file://<payload>.json   # {UserPoolId, ManagedLoginBrandingId, UseCognitoProvidedValues:false, Settings, Assets}
```

Flip a domain to v2 (idempotent; CloudFront/DNS unchanged):

```bash
aws cognito-idp update-user-pool-domain --region eu-north-1 \
  --domain login.futureready.ai --user-pool-id eu-north-1_KPb1pLiZy \
  --managed-login-version 2 \
  --custom-domain-config CertificateArn=arn:aws:acm:us-east-1:911167898745:certificate/cb17c532-7723-425a-9074-ce1307041807
```

## Rollback

- Per-client branding: `aws cognito-idp delete-managed-login-branding --user-pool-id <pool>
  --managed-login-branding-id <id>` (client falls back to Cognito's default v2 look).
- Whole surface: set `--managed-login-version 1` on the domain to return to the classic Hosted UI.
  We are staying on Cognito, so this is low-risk (master ticket §7).
