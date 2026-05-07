
**MIT**

Minkyu, Ivan, Tristan

No-SQL Final Project

# Subject: Text-focused Social Media

---

## Usage of Each DBs

**MongoDB**

Stores Posts of Users

**Neo4j**

Stores Relations of Users (e.g. following, blocking, close friends)

**Redis**

Storing Session Tokens with TTL (time to live)

---

## Key Features

- See how many hops to reach a certain person
- Usage of neo4j, instead of joining everything with Mongo
- Text-focused social media, where people can discuss their thoughts
- Like-counts using mongoDB aggregation
- MongoDB: atlas search (%search) on users posts
- Neo4j: Recommended posts for each users
- Redis: Real-time notifications

---

## Key Stack

- Python
- Flask
- Docker

---

## Getting Started

**Prerequisites**: Docker and Docker Compose installed.

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start everything (app + databases)
docker compose up -d --build

# 3. Run a data seed script
python data_seed.py
```

The API will be available at `http://localhost:8000`.

To view logs:
```bash
docker compose logs -f app
```

To stop:
```bash
docker compose down -v
```


**Project Report**

Project Idea: Text-focused Social Media. Allow users communicate with each other writing posts, like content, follow each other and explore our post recommendation system.

**Database Use Cases:** 

**MongoDB:**

**Aggregation Pipelines Used:**

    1. get_latest_post_per_user()
        Purpose: Retrieves the most recent post for each user in a list of user IDs. Efficiently solves the "latest post per user" problem using grouping and sorting without multiple queries.

    2. search_posts_by_users()
        Performs a fuzzy full-text search on post content restricted to specific users. Combines Atlas Search with filtering for high-performance, relevant results.

    3. search_posts()
        This pipeline performs a fuzzy full-text search across all posts in the database using MongoDB Atlas Search. It searches within the content field of each post document and returns the most relevant results based on the user's search query.


**Neo4j:**

We use Neo4j to model social relationships and interactions. Graph databases excel at handling highly connected data like follows, likes, and recommendations.

Path Traversal Query – Friend-of-Friend Recommendations:

This is a variable-length path traversal ([:FOLLOWS*2]) that finds users who are two degrees away (friends of friends). It excludes users the current person already follows and themselves. It implements a classic social network recommendation engine — suggesting relevant people to follow based on mutual connections. This query runs efficiently in Neo4j thanks to its graph-optimized index-free adjacency.
    

**Redis:** 

Redis serves as a high-performance layer for session management, real-time features, and temporary data.

**Data Types Used:**

    Strings: Session data, token blocklist entries
    Sets: Tracking multiple active sessions per user (user_sessions:{user_id})
    Sorted Sets: User notification inboxes (inbox:{user_id}) ordered by timestamp
    Publish/Subscribe: Real-time notification broadcasting

**Session Management (Temporary Data + Caching):**

    1. Stores active user sessions with 30-day TTL
    2. Enables fast session lookup and "logout from all devices"
    3. Token blocklist for invalidated JWTs

**Real-time Notifications (Temporary Data):**

    1. Stores latest 50 notifications per user in a Sorted Set
    2. Automatically trims old notifications
    3. Uses Pub/Sub for live updates