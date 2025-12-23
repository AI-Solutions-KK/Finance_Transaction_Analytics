#!/bin/bash

echo "Starting FastAPI..."
uvicorn backend.api:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit..."
streamlit run frontend/Home.py \
  --server.port 8501 \
  --server.address 0.0.0.0
