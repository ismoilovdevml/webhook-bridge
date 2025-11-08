#!/bin/bash

# Webhook Bridge - Environment Setup Script
# Auto-generates secure .env file with random passwords and keys

set -e

ENV=${1:-production}
SHOW_PASSWORDS=${SHOW_PASSWORDS:-true}

echo "🔐 Generating secure environment for Webhook Bridge ($ENV)"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Generate secure random keys
echo "🔑 Generating secure keys..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ADMIN_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

# Create root .env file
cat > .env << EOF
# Webhook Bridge - Auto-generated Configuration
# Generated: $(date)
# Environment: $ENV

# Security Keys
SECRET_KEY=$SECRET_KEY
ENCRYPTION_KEY=$ENCRYPTION_KEY
WEBHOOK_SECRET=$WEBHOOK_SECRET

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_EMAIL=admin@localhost
EOF

# Create frontend .env file
mkdir -p frontend
cat > frontend/.env << EOF
VITE_BACKEND_URL=http://localhost:8000
EOF

# Set secure permissions
chmod 600 .env
chmod 600 frontend/.env

echo "✅ Environment files created successfully!"
echo ""

if [ "$SHOW_PASSWORDS" = "true" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 YOUR ADMIN CREDENTIALS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "   URL:      http://localhost:3000/login"
    echo "   Username: admin"
    echo "   Password: $ADMIN_PASSWORD"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "   • Save these credentials NOW!"
    echo "   • File permissions: 600 (owner read/write only)"
    echo "   • Never commit .env to git"
    echo "   • To view later: cat .env | grep ADMIN_PASSWORD"
    echo ""
fi

echo "🚀 Next Steps:"
echo ""
echo "   1. Start services:"
echo "      docker-compose up -d"
echo ""
echo "   2. Check logs:"
echo "      docker-compose logs -f"
echo ""
echo "   3. Access application:"
echo "      http://localhost:3000"
echo ""
echo "   4. View admin password:"
echo "      cat .env | grep ADMIN_PASSWORD"
echo ""
echo "✨ Setup complete!"
