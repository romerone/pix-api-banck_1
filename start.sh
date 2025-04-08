#!/bin/sh
pip install -r requirements.txt && 
uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 30