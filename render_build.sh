#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate

echo "Seeding high-quality products into the database..."
python seed_hq_products.py

echo "Adding hoodie back view..."
python add_hoodie_back.py

echo "Build complete! Ready for Render."
