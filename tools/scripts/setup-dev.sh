#!/bin/bash

# WeNexus Development Setup Script
# This script sets up the development environment for WeNexus

set -e

echo "🚀 Setting up WeNexus development environment..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Please install Node.js 18+"; exit 1; }
command -v java >/dev/null 2>&1 || { echo "❌ Java is required but not installed. Please install Java 17+"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python is required but not installed. Please install Python 3.11+"; exit 1; }

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Set up Java backend
echo "☕ Setting up Java backend..."
cd services/java-backend
mvn clean install -DskipTests
cd ../..

# Set up Python backend
echo "🐍 Setting up Python backend..."
cd services/python-backend
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cd ../..

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
npx husky install

# Create environment files
echo "🔐 Creating environment files..."
cp apps/web/.env.example apps/web/.env.local 2>/dev/null || echo "# Add your environment variables here" > apps/web/.env.local
cp services/java-backend/.env.example services/java-backend/.env 2>/dev/null || echo "# Add your environment variables here" > services/java-backend/.env
cp services/python-backend/.env.example services/python-backend/.env 2>/dev/null || echo "# Add your environment variables here" > services/python-backend/.env

# Build shared packages
echo "📦 Building shared packages..."
npm run build --workspace=@wenexus/types
npm run build --workspace=@wenexus/utils
npm run build --workspace=@wenexus/shared
npm run build --workspace=@wenexus/ui

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your environment variables in the .env files"
echo "2. Start the development servers:"
echo "   - Frontend: npm run dev --workspace=@wenexus/web"
echo "   - Java Backend: cd services/java-backend && mvn spring-boot:run"
echo "   - Python Backend: cd services/python-backend && source venv/bin/activate && uvicorn src.main:app --reload"
echo "3. Check the documentation in docs/ for more details"
