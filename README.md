# Social Media Project Proposal

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
```

The API will be available at `http://localhost:8000`.

To view logs:
```bash
docker compose logs -f app
```

To stop:
```bash
docker compose down
```