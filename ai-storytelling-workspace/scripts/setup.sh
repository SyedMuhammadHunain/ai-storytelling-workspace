#!/bin/bash
set -e

echo "Setting up AI Storytelling Workspace v2.0..."

# Setup Python environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Setup Node environment
if [ -d "web" ]; then
    cd web
    npm install
    cd ..
fi

echo "Setup complete!"
