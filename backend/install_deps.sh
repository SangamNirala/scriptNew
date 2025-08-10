#!/bin/bash

# Correct Installation Process for Dependencies

echo "🚀 Installing Python dependencies with correct process..."

# 1. Install emergentintegrations with special index FIRST
echo "📦 Installing emergentintegrations..."
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# 2. Install spaCy language model
echo "📦 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# 3. Install all other dependencies from clean requirements
echo "📦 Installing other dependencies..."
pip install -r requirements_clean.txt

# 4. Restart backend service
echo "🔄 Restarting backend service..."
sudo supervisorctl restart backend

echo "✅ Installation complete!"