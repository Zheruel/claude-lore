import json, base64, copy

# ---- Future Ready palette (from unified-login.html), as 8-hex RGBA ----
INK         = "0f0e1aff"
INDIGO      = "2b2065ff"
INDIGO_DEEP = "1a1442ff"
LAVENDER    = "efeafaff"
LAVENDER_RIM= "dcd2f3ff"
CREAM       = "f7f3ecff"
PAPER       = "fbf8f2ff"
ACCENT      = "c8451eff"
ACCENT_SOFT = "feebe0ff"
MUTED       = "6b6478ff"
MUTED_SOFT  = "9c95a8ff"
RULE        = "e5dfd0ff"
RULE_SOFT   = "ede8ddff"
CANVAS      = "1f1d2bff"

# Start from Cognito's merged default settings (complete, valid schema)
merged = json.load(open('/tmp/ml_merged.json'))['ManagedLoginBranding']['Settings']
base = copy.deepcopy(merged)

overrides = {
  "components": {
    "primaryButton": {"lightMode": {
        "defaults": {"backgroundColor": INDIGO_DEEP, "textColor": CREAM},
        "hover":    {"backgroundColor": INK,         "textColor": CREAM},
        "active":   {"backgroundColor": INK,         "textColor": CREAM},
        "disabled": {"backgroundColor": RULE,        "borderColor": RULE},
    }},
    "secondaryButton": {"lightMode": {
        "defaults": {"backgroundColor": PAPER,   "borderColor": RULE, "textColor": INK},
        "hover":    {"backgroundColor": CREAM,   "borderColor": INK,  "textColor": INK},
        "active":   {"backgroundColor": LAVENDER,"borderColor": INDIGO,"textColor": INDIGO},
    }},
    "form": {
        "lightMode": {"backgroundColor": PAPER, "borderColor": RULE},
        "borderRadius": 4.0,
        "backgroundImage": {"enabled": True},
        "logo": {"enabled": True, "location": "CENTER", "position": "TOP", "formInclusion": "IN"},
    },
    "pageBackground": {"image": {"enabled": True}, "lightMode": {"color": CANVAS}},
    "pageText": {"lightMode": {"bodyColor": MUTED, "headingColor": INK, "descriptionColor": MUTED}},
    "idpButton": {"standard": {"lightMode": {
        "defaults": {"backgroundColor": PAPER,    "borderColor": RULE,        "textColor": INK},
        "hover":    {"backgroundColor": CREAM,    "borderColor": INDIGO_DEEP, "textColor": INDIGO_DEEP},
        "active":   {"backgroundColor": LAVENDER, "borderColor": INDIGO,      "textColor": INDIGO},
    }}},
    "favicon": {"enabledTypes": ["SVG"]},
  },
  "componentClasses": {
    "input": {"lightMode": {"defaults": {"backgroundColor": "ffffffff", "borderColor": "d7cdb8ff"},
                            "placeholderColor": MUTED_SOFT}, "borderRadius": 2.0},
    "buttons": {"borderRadius": 2.0},
    "dropDown": {"lightMode": {
        "defaults": {"itemBackgroundColor": PAPER},
        "hover":    {"itemBackgroundColor": CREAM, "itemBorderColor": MUTED_SOFT, "itemTextColor": INK},
        "match":    {"itemBackgroundColor": LAVENDER, "itemTextColor": INDIGO},
    }, "borderRadius": 2.0},
    "focusState": {"lightMode": {"borderColor": INDIGO}},
    "inputLabel": {"lightMode": {"textColor": INK}},
    "inputDescription": {"lightMode": {"textColor": MUTED}},
    "link": {"lightMode": {"defaults": {"textColor": INDIGO}, "hover": {"textColor": ACCENT}}},
    "divider": {"lightMode": {"borderColor": RULE_SOFT}},
    "optionControls": {"lightMode": {
        "defaults": {"backgroundColor": PAPER, "borderColor": MUTED_SOFT},
        "selected": {"backgroundColor": INDIGO_DEEP, "foregroundColor": CREAM},
    }},
  },
  "categories": {"global": {"colorSchemeMode": "LIGHT", "spacingDensity": "REGULAR"},
                 "form": {"displayGraphics": False}},
}

def deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

settings = deep_merge(base, overrides)
json.dump(settings, open('/tmp/brand_settings.json','w'))

def b64(path):
    return base64.b64encode(open(path,'rb').read()).decode()

LOGO   = b64('/Users/tinzeljar/Documents/future-ready/fr-end-user-adapted/public/images/logo.png')
BG     = b64('/tmp/fr-page-background.svg')
FORMBG = b64('/tmp/fr-form-background.svg')
FAV    = b64('/Users/tinzeljar/Documents/future-ready/fr-unified-login/public/favicon.svg')

assets = []
for mode in ("LIGHT","DARK"):
    assets.append({"Category":"FORM_LOGO","ColorMode":mode,"Extension":"PNG","Bytes":LOGO})
    assets.append({"Category":"PAGE_BACKGROUND","ColorMode":mode,"Extension":"SVG","Bytes":BG})
    assets.append({"Category":"FORM_BACKGROUND","ColorMode":mode,"Extension":"SVG","Bytes":FORMBG})
    assets.append({"Category":"FAVICON_SVG","ColorMode":mode,"Extension":"SVG","Bytes":FAV})

json.dump(assets, open('/tmp/brand_assets.json','w'))
print("settings bytes:", len(json.dumps(settings)))
print("assets:", [(a['Category'],a['ColorMode'],a['Extension'],len(a['Bytes'])) for a in assets])
print("logo png bytes:", len(base64.b64decode(LOGO)), "| bg svg bytes:", len(base64.b64decode(BG)), "| favicon bytes:", len(base64.b64decode(FAV)))
