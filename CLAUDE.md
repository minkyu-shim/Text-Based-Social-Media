# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Text-focused social media platform built as a NoSQL final project (EPITA S4). Team: Minkyu, Ivan, Tristan.

## Architecture

**Polyglot database design** — three NoSQL databases, each chosen for its strengths:

| Database | Role |
|----------|------|
| **MongoDB** | Stores posts; handles like-count aggregation and full-text search via Atlas `$search` |
| **Neo4j** | Stores user relationships (following, blocking, close friends); powers hop-distance queries and post recommendations |
| **Redis** | Session tokens with TTL; real-time notifications |

**Stack**: Python, Flask or Django, Docker

## Key Features to Implement

- **Hop distance**: Given two users, compute the relationship path via Neo4j graph traversal (not Mongo joins)
- **Post recommendations**: Neo4j relationship graph drives what posts a user sees
- **Full-text search**: MongoDB Atlas `$search` on post content
- **Like counts**: MongoDB aggregation pipeline
- **Real-time notifications**: Redis pub/sub or streams
- **Session management**: Redis keys with TTL

## Development Setup

> The project is in early initialization. As infrastructure is added, update this section.

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (once requirements.txt exists)
pip install -r requirements.txt

# Run the app (once entry point exists)
python app.py

# Format code
black .
```

Docker Compose will be needed to run MongoDB, Neo4j, and Redis locally — add a `docker-compose.yml` when setting up the databases.
