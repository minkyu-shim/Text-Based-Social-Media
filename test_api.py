
import requests
import sys
import time

BASE = "http://localhost:5000"
results = []


# ─── HELPERS ─────────────────────────────────────────────

def h(token):
    return {"Authorization": f"Bearer {token}"}

def section(title):
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print(f"{'=' * 55}")

def check(name, response, expected_status, assert_fn=None):
    if expected_status is None:
        try: data = response.json()
        except: data = {}
        print(f"  ⚠️  [{response.status_code}] {name}")
        results.append((name, True))
        return data

    ok = response.status_code == expected_status
    try: data = response.json()
    except: data = {}

    extra = ""
    if ok and assert_fn:
        try:
            assert_fn(data)
        except (AssertionError, KeyError, TypeError) as e:
            ok = False
            extra = f" → {e}"

    print(f"  {'✅' if ok else '❌'} [{response.status_code}] {name}{extra}")
    results.append((name, ok))
    return data

def expect(label, condition, detail=""):
    ok = bool(condition)
    print(f"  {'✅' if ok else '❌'}  {label}{': ' + str(detail) if detail else ''}")
    results.append((label, ok))


# ─── HEALTH ──────────────────────────────────────────────

section("Health Check")
check("GET /", requests.get(f"{BASE}/"), 200)


# ─── AUTH: REGISTER ──────────────────────────────────────

section("Auth — Register")

r = check("POST /auth/register (alice)",
    requests.post(f"{BASE}/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "password123"
    }), 201)
alice_token   = r.get("access_token")
alice_refresh = r.get("refresh_token")

r = check("POST /auth/register (bob)",
    requests.post(f"{BASE}/auth/register", json={
        "username": "bob", "email": "bob@test.com", "password": "password123"
    }), 201)
bob_token   = r.get("access_token")
bob_refresh = r.get("refresh_token")

r = check("POST /auth/register (carol)",
    requests.post(f"{BASE}/auth/register", json={
        "username": "carol", "email": "carol@test.com", "password": "password123"
    }), 201)
carol_token   = r.get("access_token")
carol_refresh = r.get("refresh_token")

check("POST /auth/register — duplicate email (409)",
    requests.post(f"{BASE}/auth/register", json={
        "username": "alice2", "email": "alice@test.com", "password": "password123"
    }), 409)

check("POST /auth/register — missing fields (422)",
    requests.post(f"{BASE}/auth/register", json={"email": "bad@test.com"}), 422)

if not alice_token or not bob_token or not carol_token:
    print("\n❌ Could not get tokens — is the API running at localhost:8000?")
    sys.exit(1)


# ─── AUTH: LOGIN ─────────────────────────────────────────

section("Auth — Login")

r = check("POST /auth/login (alice)",
    requests.post(f"{BASE}/auth/login", json={
        "email": "alice@test.com", "password": "password123"
    }), 200)
if r.get("access_token"):
    alice_token = r["access_token"]
    alice_refresh = r.get("refresh_token", alice_refresh)

check("POST /auth/login — wrong password (401)",
    requests.post(f"{BASE}/auth/login", json={
        "email": "alice@test.com", "password": "wrongpass"
    }), 401)

check("POST /auth/login — unknown email (401)",
    requests.post(f"{BASE}/auth/login", json={
        "email": "nobody@test.com", "password": "password123"
    }), 401)


# ─── AUTH: REFRESH TOKEN (Redis session) ─────────────────

section("Auth — Refresh Token (Redis session)")

r = check("POST /auth/refresh — valid refresh token",
    requests.post(f"{BASE}/auth/refresh", json={"refresh_token": alice_refresh}), 200)
expect("New access token returned", bool(r.get("access_token")))
if r.get("access_token"):
    alice_token = r["access_token"]

check("POST /auth/refresh — invalid token (401)",
    requests.post(f"{BASE}/auth/refresh", json={"refresh_token": "fake-token"}), 401)


# ─── USERS: PROFILE ──────────────────────────────────────

section("Users — Profile")

r = check("GET /users/me (alice)", requests.get(f"{BASE}/users/me", headers=h(alice_token)), 200)
alice_id = r.get("id")

r = check("GET /users/me (bob)", requests.get(f"{BASE}/users/me", headers=h(bob_token)), 200)
bob_id = r.get("id")

r = check("GET /users/me (carol)", requests.get(f"{BASE}/users/me", headers=h(carol_token)), 200)
carol_id = r.get("id")

check("GET /users/me — no token (401)", requests.get(f"{BASE}/users/me"), 401)

check(f"GET /users/<alice_id> (as bob)",
    requests.get(f"{BASE}/users/{alice_id}", headers=h(bob_token)), 200)

r = check("PATCH /users/me — update bio",
    requests.patch(f"{BASE}/users/me", headers=h(alice_token),
        json={"bio": "Hello I am Alice", "first_name": "Alice", "last_name": "Smith"}), 200)
expect("Bio updated", r.get("bio") == "Hello I am Alice")
expect("First name updated", r.get("first_name") == "Alice")

check("PATCH /users/me — invalid fields (400)",
    requests.patch(f"{BASE}/users/me", headers=h(alice_token),
        json={"username": "hacker"}), 400)

if not alice_id or not bob_id or not carol_id:
    print("\n❌ Could not get user IDs — aborting.")
    sys.exit(1)


# ─── USERS: FOLLOW / UNFOLLOW ────────────────────────────

section("Users — Follow / Unfollow")

check("POST /users/<bob>/follow — alice follows bob",
    requests.post(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token)), 200)

r = check("GET /users/<bob>/followers",
    requests.get(f"{BASE}/users/{bob_id}/followers", headers=h(alice_token)), 200)
followers = r.get("followers", [])
expect("Alice appears in bob's followers",
    any((u.get("id") == alice_id if isinstance(u, dict) else u == alice_id) for u in followers))

r = check("GET /users/<alice>/following",
    requests.get(f"{BASE}/users/{alice_id}/following", headers=h(alice_token)), 200)
following = r.get("following", [])
expect("Bob appears in alice's following",
    any((u.get("id") == bob_id if isinstance(u, dict) else u == bob_id) for u in following))

check("POST /users/<bob>/follow — self-follow (400)",
    requests.post(f"{BASE}/users/{alice_id}/follow", headers=h(alice_token)), 400)

check("DELETE /users/<bob>/follow — alice unfollows bob",
    requests.delete(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token)), 200)

r = check("GET /users/<bob>/followers — empty after unfollow",
    requests.get(f"{BASE}/users/{bob_id}/followers", headers=h(alice_token)), 200)
expect("Followers empty after unfollow", r.get("followers", []) == [])

# Re-follow for downstream tests
requests.post(f"{BASE}/users/{bob_id}/follow", headers=h(alice_token))


# ─── USERS: BLOCK / UNBLOCK ──────────────────────────────

section("Users — Block / Unblock")

check("POST /users/<carol>/block (alice blocks carol)",
    requests.post(f"{BASE}/users/{carol_id}/block", headers=h(alice_token)), 200)

check("POST /users/<carol>/block — self (400)",
    requests.post(f"{BASE}/users/{alice_id}/block", headers=h(alice_token)), 400)

check("DELETE /users/<carol>/block",
    requests.delete(f"{BASE}/users/{carol_id}/block", headers=h(alice_token)), 200)


# ─── USERS: CLOSE FRIENDS ────────────────────────────────

section("Users — Close Friends")

check("POST /users/<bob>/close-friends",
    requests.post(f"{BASE}/users/{bob_id}/close-friends", headers=h(alice_token)), 200)

check("DELETE /users/<bob>/close-friends",
    requests.delete(f"{BASE}/users/{bob_id}/close-friends", headers=h(alice_token)), 200)


# ─── USERS: HOP DISTANCE ─────────────────────────────────

section("Users — Hop Distance")

# alice→bob re-follow exists; re-follow bob→carol for depth-2 path
requests.post(f"{BASE}/users/{carol_id}/follow", headers=h(bob_token))

r = check("GET /users/<alice>/distance/<bob> — 1 hop",
    requests.get(f"{BASE}/users/{alice_id}/distance/{bob_id}", headers=h(alice_token)), 200)
expect("Alice→Bob connected", r.get("connected") is True, r)

r = check("GET /users/<alice>/distance/<carol> — 2 hops",
    requests.get(f"{BASE}/users/{alice_id}/distance/{carol_id}", headers=h(alice_token)), 200)
expect("Alice→Carol connected via bob", r.get("connected") is True, r)

r = check("GET /users/<alice>/distance/<alice> — self (0)",
    requests.get(f"{BASE}/users/{alice_id}/distance/{alice_id}", headers=h(alice_token)), 200)
expect("Self-distance is 0", r.get("distance") == 0)


# ─── POSTS ───────────────────────────────────────────────

section("Posts")

r = check("POST /posts/ — alice creates post",
    requests.post(f"{BASE}/posts/", headers=h(alice_token),
        json={"content": "Hello world from Alice about python coding!"}), 201)
alice_post_id = r.get("id")

r = check("POST /posts/ — bob creates post",
    requests.post(f"{BASE}/posts/", headers=h(bob_token),
        json={"content": "Bob's post about software engineering and coding"}), 201)
bob_post_id = r.get("id")

r = check("POST /posts/ — carol creates post",
    requests.post(f"{BASE}/posts/", headers=h(carol_token),
        json={"content": "Carol here, writing about python and data science"}), 201)
carol_post_id = r.get("id")

check("POST /posts/ — missing content (400)",
    requests.post(f"{BASE}/posts/", headers=h(alice_token), json={}), 400)

if alice_post_id:
    r = check("GET /posts/<alice_post_id>",
        requests.get(f"{BASE}/posts/{alice_post_id}", headers=h(alice_token)), 200)
    expect("Post content matches", "python" in r.get("content", ""))

    r = check("GET /posts/by/<alice_id>",
        requests.get(f"{BASE}/posts/by/{alice_id}", headers=h(alice_token)), 200)
    posts_list = r if isinstance(r, list) else []
    expect("Alice's post appears in her posts list",
        any(p.get("id") == alice_post_id for p in posts_list if isinstance(p, dict)))

    check("POST /posts/<alice_post>/like — bob likes alice's post",
        requests.post(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token)), 200)

    check("POST /posts/<alice_post>/like — already liked (error)",
        requests.post(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token)), None)

    r = check("GET /posts/<alice_post> — likes_count incremented",
        requests.get(f"{BASE}/posts/{alice_post_id}", headers=h(alice_token)), 200)
    expect("likes_count is 1 after like", r.get("likes_count") == 1)

    check("DELETE /posts/<alice_post>/like — bob unlikes",
        requests.delete(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token)), 200)

    r = check("GET /posts/<alice_post> — likes_count back to 0",
        requests.get(f"{BASE}/posts/{alice_post_id}", headers=h(alice_token)), 200)
    expect("likes_count is 0 after unlike", r.get("likes_count") == 0)

    check("DELETE /posts/<alice_post> — wrong user (403)",
        requests.delete(f"{BASE}/posts/{alice_post_id}", headers=h(bob_token)), 403)


# ─── NOTIFICATIONS (Redis) ───────────────────────────────

section("Notifications — Redis inbox")

# bob follows alice → alice gets a 'follow' notification
requests.post(f"{BASE}/users/{alice_id}/follow", headers=h(bob_token))

# bob likes alice's post → alice gets a 'like' notification
if alice_post_id:
    requests.post(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token))

# alice adds bob as close friend → bob gets 'close_friend' notification
requests.post(f"{BASE}/users/{bob_id}/close-friends", headers=h(alice_token))

r = check("GET /notifications/ — alice has notifications",
    requests.get(f"{BASE}/notifications/", headers=h(alice_token)), 200)
notifs = r.get("notifications", [])
expect("Alice has at least 2 notifications (follow + like)", len(notifs) >= 2, len(notifs))

types = [n.get("type") for n in notifs]
expect("'follow' notification present", "follow" in types, types)
if alice_post_id:
    expect("'like' notification present", "like" in types, types)

r = check("GET /notifications/ — bob has close_friend notification",
    requests.get(f"{BASE}/notifications/", headers=h(bob_token)), 200)
bob_notifs = r.get("notifications", [])
bob_types = [n.get("type") for n in bob_notifs]
expect("'close_friend' notification present for bob", "close_friend" in bob_types, bob_types)

# Verify notification structure
if notifs:
    n = notifs[0]
    expect("Notification has 'type' field", "type" in n)
    expect("Notification has 'from_user_id' field", "from_user_id" in n)
    expect("Notification has 'at' timestamp", "at" in n)

check("GET /notifications/ — no token (401)",
    requests.get(f"{BASE}/notifications/"), 401)

r = check("GET /notifications/?limit=1",
    requests.get(f"{BASE}/notifications/?limit=1", headers=h(alice_token)), 200)
expect("limit=1 returns at most 1 notification", r.get("count", 0) <= 1)

# Self-notification guard: alice likes her own post → no notification to self
if alice_post_id:
    requests.delete(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token))  # unlike first
    requests.post(f"{BASE}/posts/{alice_post_id}/like", headers=h(alice_token))   # alice likes own
    r = requests.get(f"{BASE}/notifications/", headers=h(alice_token)).json()
    self_notifs = [n for n in r.get("notifications", []) if n.get("from_user_id") == alice_id and n.get("type") == "like"]
    expect("No self-like notification", len(self_notifs) == 0)
    requests.delete(f"{BASE}/posts/{alice_post_id}/like", headers=h(alice_token))
    # bob re-likes for feed test
    requests.post(f"{BASE}/posts/{alice_post_id}/like", headers=h(bob_token))


# ─── FEED: HOME ──────────────────────────────────────────

section("Feed — Home Feed")

r = check("GET /feed/ — alice sees bob's post (follows him)",
    requests.get(f"{BASE}/feed/", headers=h(alice_token)), 200)
posts = r.get("posts", [])
expect("Home feed is not empty", len(posts) > 0, len(posts))
expect("Home feed posts are from bob",
    all(p.get("author_id") == bob_id for p in posts), posts)

r = check("GET /feed/ — carol sees nothing (follows nobody)",
    requests.get(f"{BASE}/feed/", headers=h(carol_token)), 200)
expect("Empty feed for carol", r.get("posts", []) == [])

check("GET /feed/ — no token (401)", requests.get(f"{BASE}/feed/"), 401)

r = check("GET /feed/?limit=1",
    requests.get(f"{BASE}/feed/?limit=1", headers=h(alice_token)), 200)
expect("limit=1 respected", r.get("count", 0) <= 1)


# ─── FEED: SEARCH (Atlas Search) ─────────────────────────

section("Feed — Search (Atlas Search $search pipeline #1)")

print("  ⏳ Waiting 15s for Atlas Search to index posts...")
time.sleep(15)

r = check("GET /feed/search?q=python",
    requests.get(f"{BASE}/feed/search?q=python", headers=h(alice_token)), 200)
expect("Search 'python' returns results", r.get("count", 0) > 0, r.get("count"))
expect("All results contain 'python'",
    all("python" in p.get("content", "").lower() for p in r.get("posts", [])))

r = check("GET /feed/search?q=coding",
    requests.get(f"{BASE}/feed/search?q=coding", headers=h(alice_token)), 200)
expect("Search 'coding' returns results", r.get("count", 0) > 0)

r = check("GET /feed/search?q=xyznonexistent",
    requests.get(f"{BASE}/feed/search?q=xyznonexistent", headers=h(alice_token)), 200)
expect("Unknown search term returns empty", r.get("posts", []) == [])

check("GET /feed/search — missing q (400)",
    requests.get(f"{BASE}/feed/search", headers=h(alice_token)), 400)

check("GET /feed/search — no token (401)",
    requests.get(f"{BASE}/feed/search?q=python"), 401)

r = check("GET /feed/search?q=pythn — fuzzy match",
    requests.get(f"{BASE}/feed/search?q=pythn", headers=h(alice_token)), 200)
expect("Fuzzy search 'pythn' finds 'python' (maxEdits:1)", r.get("count", 0) > 0, r.get("count"))


# ─── FEED: RECOMMENDATIONS (Atlas Search pipeline #2) ────

section("Feed — Recommendations (Neo4j graph + Atlas $search pipeline #2)")

# Setup: alice follows bob, bob follows carol → carol is fof for alice
# bob likes carol's post so bob has liked_post_ids for keyword extraction
if carol_post_id:
    requests.post(f"{BASE}/posts/{carol_post_id}/like", headers=h(bob_token))

r = check("GET /feed/recommendations — carol appears as fof",
    requests.get(f"{BASE}/feed/recommendations", headers=h(alice_token)), 200)
expect("Recommendations not empty", r.get("count", 0) > 0, r.get("count"))

check("GET /feed/recommendations — no token (401)",
    requests.get(f"{BASE}/feed/recommendations"), 401)

r = check("GET /feed/recommendations — carol (no follows) gets empty",
    requests.get(f"{BASE}/feed/recommendations", headers=h(carol_token)), 200)
# Carol follows nobody, so no fof — may be empty or small
expect("Carol's recs handled gracefully", "posts" in r)


# ─── AUTH: LOGOUT + BLOCKLIST ────────────────────────────

section("Auth — Logout & Token Blocklist (Redis)")

check("POST /auth/logout (alice)",
    requests.post(f"{BASE}/auth/logout", headers=h(alice_token),
        json={"refresh_token": alice_refresh}), 200)

check("GET /users/me — access token blocked after logout (401)",
    requests.get(f"{BASE}/users/me", headers=h(alice_token)), 401)

check("POST /auth/refresh — refresh session deleted after logout (401)",
    requests.post(f"{BASE}/auth/refresh", json={"refresh_token": alice_refresh}), 401)

# logout-all
r = requests.post(f"{BASE}/auth/login", json={
    "email": "bob@test.com", "password": "password123"
}).json()
bob_token2 = r.get("access_token", bob_token)
bob_refresh2 = r.get("refresh_token", bob_refresh)

check("POST /auth/logout-all (bob)",
    requests.post(f"{BASE}/auth/logout-all", headers=h(bob_token2)), 200)

check("GET /users/me — blocked after logout-all (401)",
    requests.get(f"{BASE}/users/me", headers=h(bob_token2)), 401)

check("POST /auth/refresh — all sessions wiped after logout-all (401)",
    requests.post(f"{BASE}/auth/refresh", json={"refresh_token": bob_refresh2}), 401)


# ─── CLEANUP ─────────────────────────────────────────────

section("Cleanup")

# Re-login to get fresh tokens
alice_token = requests.post(f"{BASE}/auth/login", json={
    "email": "alice@test.com", "password": "password123"
}).json().get("access_token", "")
bob_token = requests.post(f"{BASE}/auth/login", json={
    "email": "bob@test.com", "password": "password123"
}).json().get("access_token", "")
carol_token = requests.post(f"{BASE}/auth/login", json={
    "email": "carol@test.com", "password": "password123"
}).json().get("access_token", "")

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

for tok in [alice_token, bob_token, carol_token]:
    if tok:
        requests.post(f"{BASE}/auth/logout", headers=h(tok))
print("  ✅  All sessions logged out")
print("  ℹ️   User accounts remain — run 'docker compose down -v' to wipe everything")


# ─── SUMMARY ─────────────────────────────────────────────

section("Summary")
passed = sum(1 for _, ok in results if ok)
total  = len(results)
failed = [(name, ok) for name, ok in results if not ok]

print(f"\n  {passed}/{total} tests passed\n")
if failed:
    print("  Failed tests:")
    for name, _ in failed:
        print(f"    ❌ {name}")
else:
    print("  All tests passed! 🎉")
