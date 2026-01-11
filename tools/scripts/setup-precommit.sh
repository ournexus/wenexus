#!/bin/bash

# WeNexus Pre-commit Setup Script
# This script sets up pre-commit hooks for the WeNexus project

set -e

echo "🚀 Setting up WeNexus pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."

    # Try to install with pip first
    if command -v pip &> /dev/null; then
        pip install pre-commit
    elif command -v pip3 &> /dev/null; then
        pip3 install pre-commit
    elif command -v npm &> /dev/null; then
        npm install -g @pre-commit/cli
    else
        echo "❌ Please install pre-commit manually:"
        echo "   pip install pre-commit"
        echo "   or visit: https://pre-commit.com/#installation"
        exit 1
    fi
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Install commit-msg hook for conventional commits
echo "📝 Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Create .secrets.baseline if it doesn't exist
if [ ! -f .secrets.baseline ]; then
    echo "🔐 Creating secrets baseline..."
    # To generate a new baseline, run: pre-commit run detect-secrets --all-files > .secrets.baseline
    # The line below is commented out as it requires detect-secrets to be globally installed.
    # detect-secrets scan --baseline .secrets.baseline || echo "{}" > .secrets.baseline
    echo "⚠️  Using empty baseline - enable detect-secrets hook first"
    echo "{}" > .secrets.baseline
fi

# Run pre-commit on all files to ensure everything is working
echo "✅ Running initial pre-commit check..."
pre-commit run --all-files || {
    echo "⚠️  Some files need to be fixed. Running auto-fixes..."
    # Run again to apply fixes
    pre-commit run --all-files || echo "⚠️  Manual fixes may be required"
}

echo "✨ Pre-commit setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review any files that were automatically formatted"
echo "2. Commit your changes: git add . && git commit -m 'feat: setup pre-commit hooks'"
echo "3. All future commits will be automatically checked"
echo ""
echo "💡 Useful commands:"
echo "   pre-commit run --all-files  # Run checks on all files"
echo "   pre-commit run              # Run checks on staged files"
echo "   git commit --no-verify      # Skip hooks (emergency only)"
