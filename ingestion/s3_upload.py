# ============================================================
# s3_upload.py
# ============================================================
# WHAT THIS DOES:
#   Uploads a local file to S3 using the same hive-partitioned
#   path structure as our local data/ folder.
#
# WHY a separate file?
#   Both fetch_prices.py and fetch_sentiment.py need to upload.
#   DRY = Don't Repeat Yourself. One upload function, used by both.
# ============================================================

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Read bucket name from .env
S3_BUCKET = os.getenv("S3_BUCKET")


def get_s3_client():
    """
    Create and return a boto3 S3 client.

    boto3 automatically reads these from environment variables:
      AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION
    Which we inject via docker-compose env_file or .env.
    """
    return boto3.client("s3")


def upload_to_s3(local_filepath: Path, s3_prefix: str):
    """
    Upload a local file to S3 at the same hive-partitioned path.

    Parameters:
      local_filepath  → full Path to the local file
                        e.g. .../data/prices/year=2026/month=06/.../data.json
      s3_prefix       → top-level folder in S3 bucket
                        e.g. "prices", "news", "fear_greed"

    Result in S3:
      s3://your-bucket/prices/year=2026/month=06/day=17/hour=03/data.json

    WHY reconstruct the S3 key from local path?
      We want S3 to mirror the exact same hive structure as local.
      Spark reads both the same way — consistent layout everywhere.
    """
    if not S3_BUCKET:
        raise ValueError("Missing S3_BUCKET in .env file")

    # Extract the partition part of the path
    # local_filepath looks like: .../data/prices/year=2026/month=06/day=17/hour=03/data.json
    # We want S3 key:            prices/year=2026/month=06/day=17/hour=03/data.json
    #
    # .parts gives a tuple of each folder in the path
    # We find "year=..." and take everything from there onward
    parts = local_filepath.parts
    partition_start = next(i for i, p in enumerate(parts) if p.startswith("year="))
    partition_path = "/".join(parts[partition_start:])  # year=2026/month=.../data.json

    s3_key = f"{s3_prefix}/{partition_path}"  # prices/year=2026/.../data.json

    s3 = get_s3_client()
    s3.upload_file(str(local_filepath), S3_BUCKET, s3_key)

    print(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")