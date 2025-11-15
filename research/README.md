Research harness and experiment runner

This folder contains a lightweight, reproducible smoke experiment that demonstrates a minimal end-to-end run of the AutoDataSetBuilder pipeline:

- `experiment.py`: Small runner that ingests two public images, preprocesses them, runs labeling functions, and writes a JSON index as a smoke output.

How to run locally (requires MinIO and Postgres running, see project `docker-compose.yml`):

```bash
# Start services (run from project root)
docker-compose up -d

# Set env vars (in another terminal)
export S3_ENDPOINT_URL="http://localhost:9000"
export MINIO_ROOT_USER="minioadmin"
export MINIO_ROOT_PASSWORD="minioadmin"
export DB_URL="postgresql://autods_user:autods_password@localhost:5432/autods_db"
export RAW_BUCKET="raw"

# Run the smoke experiment
python research/experiment.py
```

CI integration: This script is intended to be a short smoke test executed in CI after integration tests pass. It is intentionally small to keep runtime low.
