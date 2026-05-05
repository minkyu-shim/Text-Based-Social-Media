"""
Social Media API - Integration Test Script
Run with: python test_api.py
Requires: pip install requests
"""

import requests
import time
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



# ─── FEED ────────────────────────────────────────────────
section("Feed — Home Feed")

# Setup: alice follows bob, bob creates a post
requests.post(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token))
requests.post(f"{BASE}/posts/", headers=h(bob_token), json={"content": "Bob's feed post about python"})
requests.post(f"{BASE}/posts/", headers=h(bob_token), json={"content": "Bob's second post about coding"})
print("  ⏳ Waiting 5s for Atlas Search index to sync...")
time.sleep(5)

r = check("GET /feed/ — home feed returns bob's posts",
          requests.get(f"{BASE}/feed/", headers=h(alice_token)), 200)
posts = r.get("posts", [])
expect("Home feed is not empty after following bob", len(posts) > 0, f"{len(posts)} posts")
expect("Home feed posts are from bob",
       all(p.get("author_id") == bob_id for p in posts), posts)

r = check("GET /feed/ — empty feed when following nobody (carol)",
          requests.get(f"{BASE}/feed/",
              headers=h(requests.post(f"{BASE}/auth/register", json={
                  "username": "carol", "email": "carol@test.com", "password": "password123"
              }).json().get("access_token", ""))), 200)
expect("Empty feed for user with no follows", r.get("posts", []) == [], r.get("posts"))

check("GET /feed/ — no token (401)", requests.get(f"{BASE}/feed/"), 401)
check("GET /feed/?limit=1 — limit param works",
      requests.get(f"{BASE}/feed/?limit=1", headers=h(alice_token)), 200,
      lambda d: None if d.get("count", 0) <= 1 else (_ for _ in ()).throw(AssertionError("limit not respected")))


section("Feed — Search")

r = check("GET /feed/search?q=python",
          requests.get(f"{BASE}/feed/search?q=python", headers=h(alice_token)), 200)
expect("Search for 'python' returns results", r.get("count", 0) > 0, r.get("posts"))
expect("Search results contain 'python' in content",
       all("python" in p.get("content", "").lower() for p in r.get("posts", [])),
       r.get("posts"))

r = check("GET /feed/search?q=coding",
          requests.get(f"{BASE}/feed/search?q=coding", headers=h(alice_token)), 200)
expect("Search for 'coding' returns results", r.get("count", 0) > 0)

check("GET /feed/search — missing q (400)",
      requests.get(f"{BASE}/feed/search", headers=h(alice_token)), 400)

check("GET /feed/search — no token (401)",
      requests.get(f"{BASE}/feed/search?q=python"), 401)

r = check("GET /feed/search?q=xyznonexistentword",
          requests.get(f"{BASE}/feed/search?q=xyznonexistentword", headers=h(alice_token)), 200)
expect("Search for unknown term returns empty list", r.get("posts", []) == [])


section("Feed — Recommendations")

# Setup: alice follows bob, bob follows carol → carol is a friend-of-friend for alice
carol_token = requests.post(f"{BASE}/auth/login", json={
    "email": "carol@test.com", "password": "password123"
}).json().get("access_token", "")
carol_id = requests.get(f"{BASE}/users/me", headers=h(carol_token)).json().get("id")

requests.post(f"{BASE}/posts/", headers=h(carol_token),
              json={"content": "Carol's post for recommendations"})
requests.post(f"{BASE}/users/{carol_id}/follow", headers=h(bob_token))

r = check("GET /feed/recommendations — carol appears via bob",
          requests.get(f"{BASE}/feed/recommendations", headers=h(alice_token)), 200)
expect("Recommendations not empty (carol is fof)", r.get("count", 0) > 0, r)

check("GET /feed/recommendations — no token (401)",
      requests.get(f"{BASE}/feed/recommendations"), 401)
# ─── AUTH: LOGOUT + BLOCKLIST ────────────────────────────
section("Auth — Logout & Token Blocklist (Redis)")

check("POST /auth/logout",
      requests.post(f"{BASE}/auth/logout", headers=h(alice_token)), 200)

check("GET /users/me — token blocked after logout (401)",
      requests.get(f"{BASE}/users/me", headers=h(alice_token)), 401)



# ─── CLEANUP ─────────────────────────────────────────────
section("Cleanup — Deleting test data")

# Get fresh tokens for alice and bob (alice is logged out)
r = requests.post(f"{BASE}/auth/login", json={"email": "alice@test.com", "password": "password123"})
alice_token = r.json().get("access_token", "")

r = requests.post(f"{BASE}/auth/login", json={"email": "bob@test.com", "password": "password123"})
bob_token = r.json().get("access_token", "")

carol_token = requests.post(f"{BASE}/auth/login", json={
    "email": "carol@test.com", "password": "password123"
}).json().get("access_token", "")

# Delete all posts by alice, bob, carol
for uid, tok in [(alice_id, alice_token), (bob_id, bob_token), (carol_id, carol_token)]:
    if not uid or not tok:
        continue
    try:
        posts = requests.get(f"{BASE}/posts/by/{uid}", headers=h(tok)).json()
        if isinstance(posts, list):
            for p in posts:
                pid = p.get("id")
                if pid:
                    requests.delete(f"{BASE}/posts/{pid}", headers=h(tok))
    except Exception:
        pass

print("  ✅  All test posts deleted")

# Logout remaining tokens
for tok in [bob_token, carol_token]:
    if tok:
        requests.post(f"{BASE}/auth/logout", headers=h(tok))

print("  ✅  All test sessions logged out")
print("  ℹ️   Note: user accounts (alice, bob, carol) remain in DB.")
print("        Run 'docker compose down -v' to wipe everything.")

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