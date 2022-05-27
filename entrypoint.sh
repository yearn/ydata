#!/bin/bash
cd src
python crawler.py &
uvicorn app:app --reload --proxy-headers --host 0.0.0.0