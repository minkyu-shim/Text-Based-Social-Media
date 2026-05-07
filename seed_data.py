"""
Data seed for Text-Based Social Media.

Wipes Mongo + Neo4j + Redis, then populates a realistic medium-sized dataset
(~30 users, ~150 posts, follows / blocks / close-friends / likes) by hitting the
running API at BASE.

Usage:
    # Make sure the API is up (docker compose up, or `python run.py`)
    python seed_data.py

Notes:
- Connects directly to the databases ONLY for the wipe step (uses the same
  config as the app via app.config.Config). Everything else goes through HTTP,
  matching the style of test_api.py.
- Idempotent in the sense that you can re-run it; it always wipes first.
"""

import os
import random
import sys
import time
from datetime import datetime

import requests

# Load app config so we hit the same DBs the API uses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import Config  # noqa: E402

# ─── CONFIG ──────────────────────────────────────────────────────────────────

BASE = os.getenv("SEED_API_BASE", "http://localhost:8000")

NUM_USERS = 30
NUM_POSTS = 150
FOLLOWS_PER_USER_RANGE = (3, 10)        # min/max followings per user
BLOCKS_PER_USER_RANGE = (0, 2)
CLOSE_FRIENDS_PER_USER_RANGE = (0, 3)
LIKES_PER_USER_RANGE = (5, 20)

PASSWORD = "password123"

random.seed(42)


# ─── SAMPLE DATA ─────────────────────────────────────────────────────────────

USERNAMES = [
    "alice", "bob", "carol", "dave", "eve", "frank", "grace", "henry",
    "ivy", "jack", "kate", "liam", "mia", "noah", "olivia", "peter",
    "quinn", "rachel", "sam", "tina", "ulysses", "vera", "walter", "xena",
    "yara", "zach", "amelia", "benji", "chloe", "diego",
]

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Henry",
    "Ivy", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia", "Peter",
    "Quinn", "Rachel", "Sam", "Tina", "Ulysses", "Vera", "Walter", "Xena",
    "Yara", "Zach", "Amelia", "Benji", "Chloe", "Diego",
]

LAST_NAMES = [
    "Anderson", "Brown", "Clark", "Davis", "Evans", "Foster", "Garcia",
    "Hill", "Irwin", "Jones", "King", "Lopez", "Miller", "Nelson", "Owens",
    "Parker", "Quinn", "Reed", "Smith", "Taylor", "Underwood", "Vargas",
    "Walker", "Xu", "Young", "Zimmerman", "Adams", "Bell", "Cox", "Diaz",
]

BIOS = [
    "Coffee enthusiast and weekend hiker.",
    "Building things on the internet.",
    "Books, cats, and long walks.",
    "Just here for the memes.",
    "Photographer chasing golden hour.",
    "Engineer by day, gamer by night.",
    "Plant parent. 47 and counting.",
    "Trying new recipes every week.",
    "Runner. Reader. Dreamer.",
    "Ask me about my dog.",
    "Music makes everything better.",
    "Always learning, always shipping.",
    "Tea over coffee, fight me.",
    "Travel addict on a budget.",
    "Writing more, scrolling less.",
    None, None, None,  # some users without bio
]

POST_TEMPLATES = [
    "Just finished reading {book}. Highly recommend!",
    "Hot take: {opinion}",
    "Trying out {tech} this weekend. Wish me luck.",
    "Made {food} for the first time and it actually worked!",
    "Why does {thing} have to be so complicated?",
    "Currently obsessed with {hobby}.",
    "Anyone else think {topic} is underrated?",
    "Reminder: {advice}.",
    "Spent the whole day on {activity}. Worth it.",
    "{place} in autumn hits different.",
    "Shipped a small side project today. Felt good.",
    "Coffee count: {count}. Send help.",
    "TIL: {fact}.",
    "Underrated productivity hack: {hack}.",
    "Watching {show} again. Still holds up.",
    "Anyone have good {thing} recommendations?",
    "Going off-grid this weekend. See you Monday.",
    "Just learned that {fact}. Mind = blown.",
    "Is it just me or is {thing} actually fine?",
    "Quiet morning, full inbox. Classic Monday.",
]

FILLERS = {
    "book": ["Project Hail Mary", "Dune", "The Pragmatic Programmer", "Educated", "Klara and the Sun", "Designing Data-Intensive Applications"],
    "opinion": ["pineapple belongs on pizza", "tabs > spaces", "early mornings are overrated", "podcasts are the new radio", "REST is fine, actually"],
    "tech": ["Neo4j", "Rust", "Svelte", "MongoDB Atlas Search", "Redis Streams", "Kubernetes", "WebGPU"],
    "food": ["sourdough", "ramen from scratch", "miso glazed eggplant", "homemade pasta", "kimchi", "crepes"],
    "thing": ["timezone math", "JavaScript bundlers", "airline pricing", "CSS centering", "regex", "OAuth flows"],
    "hobby": ["bouldering", "pottery", "film photography", "bird watching", "chess", "fermentation"],
    "topic": ["pair programming", "static site generators", "graph databases", "the oxford comma", "documentation"],
    "advice": ["drink water", "go outside", "back up your data", "log off occasionally", "ask the dumb question"],
    "activity": ["debugging one bug", "reading", "cleaning my flat", "writing tests", "rewriting my README"],
    "place": ["Berlin", "Lisbon", "Tokyo", "Paris", "Edinburgh", "Montreal"],
    "count": ["3", "5", "7", "9", "an embarrassing amount"],
    "fact": [
        "octopuses have three hearts",
        "honey never spoils",
        "bananas are berries",
        "Nintendo started as a playing card company",
        "MongoDB uses BSON, not JSON, internally",
    ],
    "hack": ["close all your tabs", "write the email, send it tomorrow", "name your variables longer", "do the small thing first"],
    "show": ["The Bear", "Severance", "Andor", "Better Call Saul", "Fleabag"],
}


def render_post():
    template = random.choice(POST_TEMPLATES)
    out = template
    for key, choices in FILLERS.items():
        token = "{" + key + "}"
        if token in out:
            out = out.replace(token, random.choice(choices))
    return out


# ─── HTTP HELPERS ────────────────────────────────────────────────────────────

def h(token):
    return {"Authorization": f"Bearer {token}"}


def post(path, token=None, json=None, expect=None):
    headers = h(token) if token else {}
    r = requests.post(f"{BASE}{path}", json=json, headers=headers, timeout=10)
    if expect and r.status_code != expect:
        print(f"  ⚠️  POST {path} → {r.status_code}: {r.text[:200]}")
    return r


def patch(path, token, json=None, expect=None):
    r = requests.patch(f"{BASE}{path}", json=json, headers=h(token), timeout=10)
    if expect and r.status_code != expect:
        print(f"  ⚠️  PATCH {path} → {r.status_code}: {r.text[:200]}")
    return r


# ─── WIPE ────────────────────────────────────────────────────────────────────

# def wipe_databases():
#     """Clear Mongo + Neo4j + Redis directly."""
#     print("\n🧹 Wiping databases...")

#     # Mongo
#     from pymongo import MongoClient
#     mongo = MongoClient(Config.MONGO_URI)
#     db = mongo[Config.MONGO_DB]
#     deleted_users = db["users"].delete_many({}).deleted_count
#     deleted_posts = db["posts"].delete_many({}).deleted_count
#     print(f"  ✓ Mongo: {deleted_users} users, {deleted_posts} posts deleted")
#     mongo.close()

#     # Neo4j
#     from neo4j import GraphDatabase
#     driver = GraphDatabase.driver(
#         Config.NEO4J_URI,
#         auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
#     )
#     with driver.session() as s:
#         s.run("MATCH (n) DETACH DELETE n")
#     driver.close()
#     print("  ✓ Neo4j: all nodes & relationships deleted")

#     # Redis (only our keyspaces; leave anything else alone)
#     import redis as redis_lib
#     r = redis_lib.from_url(Config.REDIS_URL, decode_responses=True)
#     keys_to_delete = []
#     for pattern in ("session:*", "user_sessions:*", "blocklist:*", "inbox:*"):
#         keys_to_delete.extend(r.keys(pattern))
#     if keys_to_delete:
#         r.delete(*keys_to_delete)
#     print(f"  ✓ Redis: {len(keys_to_delete)} keys deleted")
#     r.close()


# ─── SEED STEPS ──────────────────────────────────────────────────────────────

def wait_for_api(retries=20, delay=0.5):
    print(f"\n⏳ Waiting for API at {BASE}...")
    for _ in range(retries):
        try:
            r = requests.get(f"{BASE}/", timeout=2)
            if r.status_code == 200:
                print("  ✓ API is up")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
    print(f"  ❌ API not reachable at {BASE}. Start it first.")
    sys.exit(1)


def register_users():
    print(f"\n👥 Registering {NUM_USERS} users...")
    users = []
    usernames = USERNAMES[:NUM_USERS]
    for i, username in enumerate(usernames):
        body = {
            "username": username,
            "email": f"{username}@test.com",
            "password": PASSWORD,
        }
        r = post("/auth/register", json=body)
        if r.status_code != 201:
            print(f"  ❌ {username}: {r.status_code} {r.text[:120]}")
            continue
        data = r.json()
        token = data["access_token"]

        # /users/me to grab the id
        me = requests.get(f"{BASE}/users/me", headers=h(token), timeout=10).json()
        users.append({
            "id": me["id"],
            "username": username,
            "email": body["email"],
            "token": token,
            "first_name": FIRST_NAMES[i],
            "last_name": LAST_NAMES[i],
            "bio": random.choice(BIOS),
        })
    print(f"  ✓ {len(users)} users registered")
    return users


def update_profiles(users):
    print(f"\n📝 Updating {len(users)} profiles...")
    n = 0
    for u in users:
        updates = {"first_name": u["first_name"], "last_name": u["last_name"]}
        if u["bio"]:
            updates["bio"] = u["bio"]
        r = patch("/users/me", u["token"], json=updates)
        if r.status_code == 200:
            n += 1
    print(f"  ✓ {n} profiles updated")


def create_follows(users):
    print(f"\n🔗 Creating follow relationships...")
    n = 0
    for u in users:
        candidates = [other for other in users if other["id"] != u["id"]]
        k = random.randint(*FOLLOWS_PER_USER_RANGE)
        k = min(k, len(candidates))
        for target in random.sample(candidates, k):
            r = post(f"/users/{target['id']}/follow", token=u["token"])
            if r.status_code == 200:
                n += 1
    print(f"  ✓ {n} follows created")


def create_blocks(users):
    print(f"\n🚫 Creating blocks...")
    n = 0
    for u in users:
        candidates = [other for other in users if other["id"] != u["id"]]
        k = random.randint(*BLOCKS_PER_USER_RANGE)
        k = min(k, len(candidates))
        if k == 0:
            continue
        for target in random.sample(candidates, k):
            r = post(f"/users/{target['id']}/block", token=u["token"])
            if r.status_code == 200:
                n += 1
    print(f"  ✓ {n} blocks created")


def create_close_friends(users):
    print(f"\n💚 Creating close-friend relationships...")
    n = 0
    for u in users:
        candidates = [other for other in users if other["id"] != u["id"]]
        k = random.randint(*CLOSE_FRIENDS_PER_USER_RANGE)
        k = min(k, len(candidates))
        if k == 0:
            continue
        for target in random.sample(candidates, k):
            r = post(f"/users/{target['id']}/close-friends", token=u["token"])
            if r.status_code == 200:
                n += 1
    print(f"  ✓ {n} close-friend relationships created")


def create_posts(users):
    print(f"\n📮 Creating {NUM_POSTS} posts...")
    posts = []
    for _ in range(NUM_POSTS):
        author = random.choice(users)
        content = render_post()
        r = post("/posts/", token=author["token"], json={"content": content})
        if r.status_code == 201:
            data = r.json()
            posts.append({"id": data["id"], "author_id": author["id"]})
    print(f"  ✓ {len(posts)} posts created")
    return posts


def create_likes(users, posts):
    print(f"\n❤️  Creating likes...")
    n = 0
    for u in users:
        # users can't like their own (well, they can, but it's weird) — exclude
        likeable = [p for p in posts if p["author_id"] != u["id"]]
        k = random.randint(*LIKES_PER_USER_RANGE)
        k = min(k, len(likeable))
        if k == 0:
            continue
        for p in random.sample(likeable, k):
            r = post(f"/posts/{p['id']}/like", token=u["token"])
            if r.status_code == 200:
                n += 1
    print(f"  ✓ {n} likes created")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    started = datetime.now()
    print("=" * 60)
    print("  SEED — Text-Based Social Media")
    print(f"  API: {BASE}")
    print("=" * 60)

    #wipe_databases()
    wait_for_api()

    users = register_users()
    if not users:
        print("\n❌ No users created — aborting.")
        sys.exit(1)

    update_profiles(users)
    create_follows(users)
    create_blocks(users)
    create_close_friends(users)
    posts = create_posts(users)
    create_likes(users, posts)

    elapsed = (datetime.now() - started).total_seconds()
    print("\n" + "=" * 60)
    print(f"  ✅ Seed complete in {elapsed:.1f}s")
    print("=" * 60)
    print("\n  Sample logins (password = 'password123'):")
    for u in users[:5]:
        print(f"    • {u['email']}  (id: {u['id']})")
    print()


if __name__ == "__main__":
    main()