#!/bin/bash

# Credible Project - Autonomus Hack 26 Deployment Script
# Project: autonomus-hack-26

echo "🚀 Deploying Credible to Google Cloud Platform..."
echo "================================================="

# Set project
echo "📌 Setting GCP project..."
gcloud config set project autonomus-hack-26

# Check if app.yaml exists
if [ ! -f "app.yaml" ]; then
    echo "❌ app.yaml not found! Creating one..."
    cat > app.yaml << 'EOF'
runtime: python312

instance_class: F2

env_variables:
  SECRET_KEY: 'django-insecure-3&sutc15)!x_fj$u7pi@+5x&r3ile24!r64x&l)n#-r4$ue&#+'
  DEBUG: 'True'
  DJANGO_SETTINGS_MODULE: 'credible.settings'

handlers:
- url: /static
  static_dir: static/

- url: /media
  static_dir: media/

- url: /.*
  script: auto

entrypoint: gunicorn -b :$PORT --workers 2 --threads 4 --timeout 60 credible.wsgi:application

automatic_scaling:
  min_instances: 0
  max_instances: 10
EOF
    echo "✅ app.yaml created!"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt not found! Creating basic one..."
    cat > requirements.txt << 'EOF'
Django>=4.2.0
gunicorn>=21.2.0
EOF
    echo "✅ requirements.txt created!"
fi

# Create static directory if it doesn't exist
if [ ! -d "static" ]; then
    echo "📁 Creating static directory..."
    mkdir static
fi

# Collect static files
echo "📦 Collecting static files..."
python3 manage.py collectstatic --noinput

# Check if collectstatic succeeded
if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully!"
else
    echo "⚠️  Warning: collectstatic had issues, continuing anyway..."
fi

# Deploy to App Engine
echo ""
echo "☁️  Deploying to App Engine..."
echo "This may take 5-10 minutes..."
gcloud app deploy --project=autonomus-hack-26 --quiet

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "================================================="
    echo "🌐 Your app is live at:"
    echo "   https://autonomus-hack-26.uc.r.appspot.com"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    gcloud app logs tail"
    echo "   Open browser: gcloud app browse"
    echo "   Check status: gcloud app describe"
    echo "================================================="
    
    # Open in browser
    read -p "🌐 Open app in browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud app browse --project=autonomus-hack-26
    fi
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Checking logs..."
    gcloud app logs read --limit=20
fi