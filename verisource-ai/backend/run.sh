#!/usr/bin/env bash
# =============================================================================
# VeriSource AI — Development Server Launcher
# =============================================================================
# These env vars MUST be exported at OS level BEFORE Python starts.
# Setting them inside main.py is too late — native C++ extensions (hnswlib,
# OpenMP, MKL, BLAS) initialise their thread pools on first import, before
# any Python code in main.py runs.
# =============================================================================

set -e

export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# ⚠️  No --reload: reload spawns a file-watcher parent process that also
# imports all modules, causing a second ChromaDB client to open the same
# SQLite WAL file and trigger hnswlib mutex contention.
# Use this for development; restart manually when you change code.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
