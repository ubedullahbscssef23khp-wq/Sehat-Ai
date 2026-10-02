#!/bin/bash
set -e
cd backend
rm -rf .venv
if ! which virtualenv >/dev/null 2>&1; then
  if ! which pip >/dev/null 2>&1 && ! which pip3 >/dev/null 2>&1; then
    if [ -f "../get-pip.py" ]; then
      python3 ../get-pip.py --user
    else
      curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
      python3 /tmp/get-pip.py --user
    fi
  fi
  /root/.local/bin/pip install virtualenv || pip install virtualenv || true
fi
python3 -m virtualenv .venv
.venv/bin/pip install -e ".[dev]"
