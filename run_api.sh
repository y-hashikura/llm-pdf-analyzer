#!/bin/bash
PYTHONPATH=. uvicorn api.main:app --reload
