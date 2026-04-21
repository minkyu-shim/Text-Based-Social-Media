# TODO

Text-focused social media platform using MongoDB, Neo4j, and Redis.

---

## Phase 1 — Foundation

- [ ] Create `requirements.txt` with: `flask`, `pymongo[srv]`, `neo4j`, `redis`, `flask-jwt-extended`, `python-dotenv`, `pytest`, `black`
- [ ] Create `docker-compose.yml` with services: `mongodb` (port 27017), `neo4j` (ports 7474, 7687), `redis` (port 6379)
- [ ] Create `.env.example` with placeholders: `MONGO_URI`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `REDIS_URL`, `JWT_SECRET_KEY`
- [ ] Create Flask app factory in `app/__init__.py` (`create_app()`)
- [ ] Create `app/config.py` that loads variables from `.env`
- [ ] Create DB connection singletons: `app/db/mongo.py`, `app/db/neo4j.py`, `app/db/redis.py`
- [ ] Create `run.py` entry point

---

## Phase 2 — Auth

- [ ] `POST /register` — create user in MongoDB (profile data) and Neo4j (user node), return JWT
- [ ] `POST /login` — verify credentials, return JWT
- [ ] `POST /logout` — add JWT to Redis blocklist with TTL matching token expiry
- [ ] Add JWT-required middleware to protected routes (blocklist check on every request)

---

## Phase 3 — Posts

- [done] `POST /posts` — create a post (author_id, content, timestamp, likes_count: 0) in MongoDB
- [done] `GET /posts/<id>` — fetch a single post
- [ ] `DELETE /posts/<id>` — delete own post
- [done] `PUT /posts/<id>/like` — increment `likes_count` via `$inc`
- [done] `PUT /posts/<id>/like` — decrement `likes_count` via `$inc`
- [done] `GET /users/<id>/posts` — fetch all posts by a user

---

## Phase 4 — Social Graph (Neo4j)

- [ ] `POST /users/<id>/follow` — `CREATE (a)-[:FOLLOWS]->(b)`
- [ ] `DELETE /users/<id>/follow` — remove `FOLLOWS` relationship
- [ ] `POST /users/<id>/block` — `CREATE (a)-[:BLOCKS]->(b)`, remove any existing FOLLOWS in both directions
- [ ] `DELETE /users/<id>/block` — remove `BLOCKS` relationship
- [ ] `POST /users/<id>/close-friends` — `CREATE (a)-[:CLOSE_FRIENDS]->(b)`
- [ ] `DELETE /users/<id>/close-friends` — remove `CLOSE_FRIENDS` relationship
- [ ] `GET /users/<id>/followers` — list users following `<id>`
- [ ] `GET /users/<id>/following` — list users `<id>` follows
- [ ] `GET /users/<id>/distance/<target_id>` — return hop count via Neo4j `shortestPath()`

---

## Phase 5 — Feed & Discovery

- [ ] `GET /feed` — query Neo4j for followed user IDs, then fetch their recent posts from MongoDB (sorted by date)
- [ ] `GET /search?q=<query>` — full-text search on post content using MongoDB Atlas `$search`
- [ ] `GET /recommendations` — Neo4j friends-of-friends (FOLLOWS depth 2) not yet followed, fetch sample posts from MongoDB

---

## Phase 6 — Notifications (Redis)

- [ ] On follow: publish event to user's Redis channel (`notify:<user_id>`)
- [ ] On post liked: publish event to post author's Redis channel
- [ ] `GET /notifications` — fetch unread notifications from Redis list/stream for current user

---

## Cross-cutting

- [ ] Consistent JSON error responses (`{"error": "message"}`) for all routes
- [ ] Input validation on all request bodies
- [ ] Indexes: MongoDB index on `author_id` and `created_at`; Neo4j index on `User.id`
- [ ] Write `pytest` tests for each service layer (auth, posts, graph, feed)
- [ ] Update `CLAUDE.md` with final build/run/test commands once infrastructure is in place
