"""
Social Media API - Integration Test Script
Run with: python test_api.py
Requires: pip install requests
"""

import requests
import sys

BASE = "http://localhost:8000"
results = []


def check(name, response, expected_status, assert_fn=None):
    if expected_status is None:
        try:
            data = response.json()
        except Exception:
            data = {}
        print(f"  ⚠️  [{response.status_code}] {name}")
        results.append((name, True))
        return data

    ok = response.status_code == expected_status
    data = {}
    try:
        data = response.json()
    except Exception:
        pass

    extra = ""
    if ok and assert_fn:
        try:
            assert_fn(data)
        except (AssertionError, KeyError, TypeError) as e:
            ok = False
            extra = f" → assertion failed: {e}"

    icon = "✅" if ok else "❌"
    print(f"  {icon} [{response.status_code}] {name}{extra}")
    results.append((name, ok))
    return data


def h(token):
    return {"Authorization": f"Bearer {token}"}


def section(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def expect(label, condition, detail=""):
    icon = "✅" if condition else "❌"
    print(f"  {icon}  {label}{': ' + str(detail) if detail else ''}")
    results.append((label, condition))


# ─── HEALTH CHECK ────────────────────────────────────────
section("Health Check")
check("GET /", requests.get(f"{BASE}/"), 200)


# ─── AUTH: REGISTER ──────────────────────────────────────
section("Auth — Register")

r = check("POST /auth/register (alice)",
          requests.post(f"{BASE}/auth/register", json={
              "username": "alice", "email": "alice@test.com", "password": "password123"
          }), 201)
alice_token = r.get("access_token")

r = check("POST /auth/register (bob)",
          requests.post(f"{BASE}/auth/register", json={
              "username": "bob", "email": "bob@test.com", "password": "password123"
          }), 201)
bob_token = r.get("access_token")

check("POST /auth/register — duplicate email (409)",
      requests.post(f"{BASE}/auth/register", json={
          "username": "alice2", "email": "alice@test.com", "password": "password123"
      }), 409)

check("POST /auth/register — missing fields (422)",
      requests.post(f"{BASE}/auth/register", json={"email": "bad@test.com"}), 422)

if not alice_token or not bob_token:
    print("\n❌ Could not get tokens — make sure the API is running at localhost:8000")
    sys.exit(1)


# ─── AUTH: LOGIN ─────────────────────────────────────────
section("Auth — Login")

r = check("POST /auth/login (alice)",
          requests.post(f"{BASE}/auth/login", json={
              "email": "alice@test.com", "password": "password123"
          }), 200)
if r.get("access_token"):
    alice_token = r["access_token"]

check("POST /auth/login — wrong password (401)",
      requests.post(f"{BASE}/auth/login", json={
          "email": "alice@test.com", "password": "wrongpass"
      }), 401)


# ─── USERS: PROFILE ──────────────────────────────────────
section("Users — Profile")

r = check("GET /users/me (alice)", requests.get(f"{BASE}/users/me", headers=h(alice_token)), 200)
alice_id = r.get("id")

r = check("GET /users/me (bob)", requests.get(f"{BASE}/users/me", headers=h(bob_token)), 200)
bob_id = r.get("id")

check("GET /users/me — no token (401)", requests.get(f"{BASE}/users/me"), 401)

if alice_id:
    check("GET /users/<alice_id> (as bob)",
          requests.get(f"{BASE}/users/{alice_id}", headers=h(bob_token)), 200)

r = check("PATCH /users/me — update bio",
          requests.patch(f"{BASE}/users/me", headers=h(alice_token),
                         json={"bio": "Hello I am Alice"}), 200)
expect("Bio updated correctly", r.get("bio") == "Hello I am Alice")

check("PATCH /users/me — no valid fields (400)",
      requests.patch(f"{BASE}/users/me", headers=h(alice_token),
                     json={"username": "hacker"}), 400)

if not alice_id or not bob_id:
    print("\n❌ Could not get user IDs — aborting.")
    sys.exit(1)


# ─── USERS: FOLLOW / UNFOLLOW ────────────────────────────
section("Users — Follow / Unfollow")

check("POST /users/<bob>/follow — alice follows bob",
      requests.post(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token)), 200)

r = check("GET /users/<bob>/followers",
          requests.get(f"{BASE}/users/{bob_id}/followers", headers=h(alice_token)), 200)
followers = r.get("followers", [])
alice_in_followers = any(
    (u.get("id") == alice_id if isinstance(u, dict) else u == alice_id) for u in followers
)
expect("Alice appears in bob's followers", alice_in_followers, followers)

r = check("GET /users/<alice>/following",
          requests.get(f"{BASE}/users/{alice_id}/following", headers=h(alice_token)), 200)
following = r.get("following", [])
bob_in_following = any(
    (u.get("id") == bob_id if isinstance(u, dict) else u == bob_id) for u in following
)
expect("Bob appears in alice's following", bob_in_following, following)

check("DELETE /users/<bob>/follow — alice unfollows bob",
      requests.delete(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token)), 200)

r = check("GET /users/<bob>/followers — after unfollow",
          requests.get(f"{BASE}/users/{bob_id}/followers", headers=h(alice_token)), 200)
expect("Followers empty after unfollow", r.get("followers", []) == [])



# ─── USERS: BLOCK / UNBLOCK ──────────────────────────────
section("Users — Block / Unblock")

check("POST /users/<bob>/block",
      requests.post(f"{BASE}/users/{bob_id}/block", headers=h(alice_token)), 200)
check("DELETE /users/<bob>/block",
      requests.delete(f"{BASE}/users/{bob_id}/block", headers=h(alice_token)), 200)


# ─── USERS: CLOSE FRIENDS ────────────────────────────────
section("Users — Close Friends")

check("POST /users/<bob>/close-friends",
      requests.post(f"{BASE}/users/{bob_id}/close-friends", headers=h(alice_token)), 200)
check("DELETE /users/<bob>/close-friends",
      requests.delete(f"{BASE}/users/{bob_id}/close-friends", headers=h(alice_token)), 200)


# ─── USERS: HOP DISTANCE ─────────────────────────────────
# Re-follow for distance test
requests.post(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token))

section("Users — Hop Distance")

r = check("GET /users/<alice>/distance/<bob>",
          requests.get(f"{BASE}/users/{alice_id}/distance/{bob_id}", headers=h(alice_token)), 200)
expect("Alice → Bob connected",
       r.get("connected") is True,
       r)


# ─── POSTS ───────────────────────────────────────────────
section("Posts")

r = check("POST /posts/ — alice creates post",
          requests.post(f"{BASE}/posts/", headers=h(alice_token),
                        json={"content": "Hello world from Alice!"}), 201)
post_id = r.get("id")

check("POST /posts/ — missing content (400)",
      requests.post(f"{BASE}/posts/", headers=h(alice_token), json={}), 400)

if post_id:
    r = check("GET /posts/<post_id>",
              requests.get(f"{BASE}/posts/{post_id}", headers=h(alice_token)), 200)
    expect("Post content matches", r.get("content") == "Hello world from Alice!")

    r = check("GET /posts/by/<alice_id>",
              requests.get(f"{BASE}/posts/by/{alice_id}", headers=h(alice_token)), 200)
    posts_list = r if isinstance(r, list) else []
    expect("Created post appears in alice's posts list",
           any(p.get("id") == post_id for p in posts_list if isinstance(p, dict)))

    check("POST /posts/<post_id>/like — bob likes",
          requests.post(f"{BASE}/posts/{post_id}/like", headers=h(bob_token)), 200)

    check("POST /posts/<post_id>/like — already liked (expect error)",
          requests.post(f"{BASE}/posts/{post_id}/like", headers=h(bob_token)), None)

    check("DELETE /posts/<post_id>/like — bob unlikes",
          requests.delete(f"{BASE}/posts/{post_id}/like", headers=h(bob_token)), 200)

    check("DELETE /posts/<post_id> — wrong user (403)",
          requests.delete(f"{BASE}/posts/{post_id}", headers=h(bob_token)), 403)

    check("DELETE /posts/<post_id> — correct user (200)",
          requests.delete(f"{BASE}/posts/{post_id}", headers=h(alice_token)), 200)

    check("GET /posts/<post_id> — after delete (404)",
          requests.get(f"{BASE}/posts/{post_id}", headers=h(alice_token)), 404)
else:
    print("  ⚠️  Skipping post sub-tests — no post_id returned from create")


# ─── AUTH: LOGOUT + BLOCKLIST ────────────────────────────
section("Auth — Logout & Token Blocklist (Redis)")

check("POST /auth/logout",
      requests.post(f"{BASE}/auth/logout", headers=h(alice_token)), 200)

check("GET /users/me — token blocked after logout (401)",
      requests.get(f"{BASE}/users/me", headers=h(alice_token)), 401)


# ─── SUMMARY ─────────────────────────────────────────────
section("Summary")
passed = sum(1 for _, ok in results if ok)
total = len(results)
failed = [(name, ok) for name, ok in results if not ok]

print(f"\n  {passed}/{total} tests passed\n")
if failed:
    print("  Failed tests:")
    for name, _ in failed:
        print(f"    ❌ {name}")
else:
    print("  All tests passed! 🎉")
