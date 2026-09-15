"""
Run this ONCE to authorize your Instagram (Business/Creator) account and get a
long-lived access token + your Instagram user id.

Requirements before running this:
- Your Instagram account must be a Professional account (Business or Creator)
  linked to a Facebook Page.
- You created a Meta app at developers.facebook.com with "Instagram Graph API"
  / "Instagram API" product added, and have the App ID + App Secret.
- You added a valid OAuth Redirect URI in the app's settings (must match what
  you enter below exactly -- e.g. your GitHub Pages URL).
"""

import urllib.parse
import httpx

GRAPH_ROOT = "https://graph.facebook.com/v19.0"

app_id = input("Meta App ID: ").strip()
app_secret = input("Meta App Secret: ").strip()
redirect_uri = input("Redirect URI (must match your app's registered redirect URI exactly): ").strip()

scopes = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"
auth_url = (
    "https://www.facebook.com/v19.0/dialog/oauth"
    f"?client_id={urllib.parse.quote(app_id)}"
    f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
    f"&scope={urllib.parse.quote(scopes)}"
    "&response_type=code"
)

print("\n1) Open this URL in your browser and approve access with your Facebook account:\n")
print(auth_url)
print("\n2) After approving, your browser redirects to a URL containing '?code=...'.")
print("   Copy that FULL URL from the address bar and paste it below.\n")

redirected_url = input("Paste the full redirected URL here: ").strip()
code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url).query).get("code", [None])[0]
if not code:
    raise SystemExit("Could not find '?code=' in that URL.")

# Exchange code -> short-lived user access token
resp = httpx.get(
    f"{GRAPH_ROOT}/oauth/access_token",
    params={"client_id": app_id, "redirect_uri": redirect_uri, "client_secret": app_secret, "code": code},
    timeout=30,
).json()
if "access_token" not in resp:
    raise SystemExit(f"Code exchange failed: {resp}")
short_lived_token = resp["access_token"]

# Exchange short-lived -> long-lived user access token (~60 days)
resp = httpx.get(
    f"{GRAPH_ROOT}/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token,
    },
    timeout=30,
).json()
if "access_token" not in resp:
    raise SystemExit(f"Long-lived token exchange failed: {resp}")
long_lived_token = resp["access_token"]

# List the Facebook Pages this user manages, with a page access token for each
pages = httpx.get(f"{GRAPH_ROOT}/me/accounts", params={"access_token": long_lived_token}, timeout=30).json()
page_list = pages.get("data", [])
if not page_list:
    raise SystemExit(f"No Facebook Pages found for this account: {pages}")

print("\nYour Facebook Pages:")
for i, page in enumerate(page_list):
    print(f"  [{i}] {page['name']} (id: {page['id']})")

choice = int(input("\nWhich page is linked to your Instagram account? Enter the number: ").strip())
page = page_list[choice]
page_access_token = page["access_token"]

# Get the Instagram Business Account id linked to that page
ig_resp = httpx.get(
    f"{GRAPH_ROOT}/{page['id']}",
    params={"fields": "instagram_business_account", "access_token": page_access_token},
    timeout=30,
).json()
ig_account = ig_resp.get("instagram_business_account")
if not ig_account:
    raise SystemExit(
        f"No Instagram Business Account linked to page '{page['name']}': {ig_resp}\n"
        "Make sure your Instagram account is Professional and linked to this Facebook Page."
    )

print("\n=== COPY THESE — KEEP THEM SECRET ===\n")
print(f"IG_ACCESS_TOKEN={page_access_token}")
print(f"IG_USER_ID={ig_account['id']}")
print("\n=======================================")
print("Save these two as GitHub Secrets.")
print("\nNote: this page access token inherits the long-lived (~60 day) lifetime")
print("of the user token it was derived from. Re-run this script to refresh it")
print("before it expires.")
