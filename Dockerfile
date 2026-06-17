# ============================================================
# Dockerfile
# ============================================================
# WHAT THIS IS:
#   A recipe that builds a container image for our ingestion scripts.
#   Docker reads this top-to-bottom to create a reproducible environment.
#
# HOW TO BUILD:
#   docker build -t crypto-ingestion .
#
# HOW TO RUN:
#   docker-compose up   (preferred — handles env vars and volumes)
# ============================================================


# --- STEP 1: Choose a base image ---
# "python:3.11-slim" = official Python 3.11 on a minimal Linux OS
# "slim" = smaller than the full image (no extras we don't need)
# WHY Python 3.11: matches a stable, widely supported version
FROM python:3.11-slim


# --- STEP 2: Set working directory inside the container ---
# All following commands run from /app
# Think of this as "cd /app" inside the container
WORKDIR /app


# --- STEP 3: Copy requirements FIRST (before the rest of the code) ---
# WHY first: Docker caches each step. If requirements.txt hasn't changed,
# Docker skips re-installing packages on the next build (much faster).
COPY requirements.txt .


# --- STEP 4: Install Python packages ---
# --no-cache-dir = don't save pip's download cache (keeps image smaller)
RUN pip install --no-cache-dir -r requirements.txt


# --- STEP 5: Copy your actual code into the container ---
# "COPY . ." = copy everything from your project root into /app
# .dockerignore controls what gets excluded (venv/, data/, .env, etc.)
COPY . .


# --- STEP 6: Set default command ---
# This runs when you do "docker run crypto-ingestion"
# We run run_all.py which calls both fetch_prices and fetch_sentiment
CMD ["python", "ingestion/run_all.py"]