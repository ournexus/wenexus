# WeNexus Smart Fix Documentation

## Overview

WeNexus Smart Fix is an intelligent code quality tool that automatically fixes common issues and
progressively retries failed pre-commit hooks. It's designed to improve developer experience while
maintaining code quality standards.

## Features

### 🔧 Multi-Level Fixing

- **Safe Fixes**: Applied automatically (formatting, whitespace, etc.)
- **Interactive Fixes**: Require confirmation (TODO removal, missing exports)
- **Manual Fixes**: Only reported (type errors, security issues)

### 🔄 Progressive Retry

1. **Attempt 1**: Run pre-commit checks
2. **Attempt 2**: Apply safe fixes + retry
3. **Attempt 3**: Apply interactive fixes + retry
4. **Final**: Report manual fixes needed

### 🎯 Smart Commit

- Preserves original commit messages
- Adds fix annotations
- Configurable auto-commit behavior

## Usage

### Automatic (Recommended)

Smart Fix runs automatically during git commits via husky hooks:

```bash
git add .
git commit -m "feat: add new feature"
# Smart Fix runs automatically if pre-commit fails
```

### Manual

Run Smart Fix manually when needed:

```bash
# Run with default configuration
./tools/scripts/smart-fix.sh

# Run with specific configuration
AUTOFIX_LEVEL=interactive ./tools/scripts/smart-fix.sh
```

## Configuration

Edit `.autofix.yaml` to customize behavior:

```yaml
# Fix levels: safe, interactive, aggressive
level: safe

# Auto-commit after successful fixes
auto-commit: false

# Create backups before fixing
backup: true

# Enable detailed logging
logging: true
```

### Fix Levels

#### Safe Mode (Default)

- ✅ Prettier formatting
- ✅ ESLint auto-fix
- ✅ Whitespace cleanup
- ✅ End-of-file newlines
- ❌ No destructive changes

#### Interactive Mode

- ✅ All safe fixes
- ❓ Prompts for TODO removal
- ❓ Prompts for missing exports
- ❓ Prompts for brand consistency

#### Aggressive Mode

- ✅ All safe fixes
- ✅ All interactive fixes (no prompts)
- ⚠️ **Use with caution!**

## Smart Fix Categories

### Safe Fixes (Always Applied)

- **Prettier**: Code formatting
- **ESLint**: Auto-fixable rules
- **Whitespace**: Trailing spaces, tabs
- **Newlines**: End-of-file consistency
- **Imports**: Organization and sorting

### Interactive Fixes (Require Confirmation)

- **TODO Comments**: Remove development notes
- **Missing Exports**: Add empty exports to TypeScript files
- **Brand Consistency**: Fix WeNexus naming
- **Package.json**: Validate and fix JSON structure

### Manual Fixes (Reported Only)

- **Type Errors**: TypeScript compilation issues
- **Security Issues**: Potential vulnerabilities
- **Logic Errors**: Require human review
- **Missing Tests**: Test coverage gaps

## Integration

### Pre-commit Hooks

Smart Fix integrates with pre-commit through:

- Custom pre-commit hook (runs first)
- Husky wrapper script
- Automatic retry mechanism

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run Smart Fix
  run: |
    ./tools/scripts/smart-fix.sh
    git diff --exit-code || (git add . && git commit -m "ci: auto-fix")
```

## Troubleshooting

### Common Issues

#### Smart Fix Not Running

```bash
# Check if scripts are executable
chmod +x tools/scripts/smart-fix.sh
chmod +x tools/scripts/precommit-wrapper.sh

# Verify pre-commit installation
pre-commit --version
```

#### Configuration Not Loading

```bash
# Check configuration file
cat .autofix.yaml

# Run with debug output
DEBUG=1 ./tools/scripts/smart-fix.sh
```

#### Backup Recovery

```bash
# List available backups
ls -la .autofix-backup/

# Restore from backup
cp -r .autofix-backup/20231215_143022/* .
```

### Emergency Bypass

If Smart Fix is causing issues:

```bash
# Skip all hooks for one commit
git commit --no-verify -m "emergency: bypass hooks"

# Disable Smart Fix temporarily
mv .autofix.yaml .autofix.yaml.disabled
```

## Best Practices

### Development Workflow

1. **Write code** normally
2. **Commit** with descriptive messages
3. **Let Smart Fix** handle quality issues
4. **Review** auto-applied changes
5. **Manually fix** reported issues

### Configuration Tips

- Start with `safe` level for new projects
- Use `interactive` for experienced teams
- Enable `auto-commit` only in trusted environments
- Keep `backup` enabled during setup

### Team Collaboration

- Commit `.autofix.yaml` to version control
- Document custom configurations
- Train team on fix levels
- Establish manual fix procedures

## Advanced Features

### Custom Fix Scripts

Add your own fixes to `smart-fix.sh`:

```bash
# Add custom safe fix
apply_custom_fixes() {
    # Your custom logic here
    log "Running custom fixes..."
}
```

### Webhook Integration

Configure webhooks for CI/CD notifications:

```yaml
notifications:
  webhook: true
  webhook-url: 'https://your-webhook.com/smart-fix'
```

### Performance Optimization

- Limit file patterns in configuration
- Use parallel processing for large codebases
- Configure appropriate timeouts

## Support

### Logs and Debugging

- Check `.autofix.log` for detailed operation logs
- Use `DEBUG=1` for verbose output
- Review backup files for change history

### Getting Help

- Check project documentation
- Review existing GitHub issues
- Contact the development team

## Changelog

### v1.0.0

- Initial release
- Safe, interactive, and aggressive fix levels
- Progressive retry mechanism
- Smart commit integration
- Comprehensive configuration options
