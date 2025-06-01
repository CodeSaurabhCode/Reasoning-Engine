#!/bin/sh

# Run the FastAPI app using uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
