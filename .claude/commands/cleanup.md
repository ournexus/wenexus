Please clean up the repository by removing stale branches and performing maintenance tasks: $ARGUMENTS.

# REPOSITORY MAINTENANCE PRINCIPLES

## Core Principles

1. **Keep It Clean**: Regular maintenance prevents technical debt accumulation
2. **Automate Where Possible**: Use scripts and CI/CD for routine tasks
3. **Document Everything**: Maintain clear records of maintenance activities
4. **Test Before & After**: Verify functionality before and after maintenance
5. **Follow Git Flow**: Maintain a clear branching strategy and workflow

## Best Practices Timeline

- **Daily**: Small cleanups during development
- **Weekly**: Branch pruning and dependency checks
- **Monthly**: Deep cleaning and optimization
- **Quarterly**: Major dependency updates and security audits

# EXECUTION PLAN

## 1. Preparation & Safety Measures

- **Create a backup branch before cleanup**:
  ```bash
  git checkout -b backup-before-cleanup-$(date +%Y%m%d)
  git checkout main
  ```

- **Document current state**:
  ```bash
  # Save current branch list for reference
  git branch -a > branch-list-before-cleanup.txt
  
  # Document current dependencies
  npm list > dependencies-before-cleanup.txt
  ```

## 2. Branch Management

- **Fetch latest updates from remote**:
  ```bash
  # Fetch all branches and prune references to deleted remote branches
  git fetch --all --prune
  ```

- **Switch to main branch and update**:
  ```bash
  git checkout main
  git pull origin main
  ```

- **Clean up local branches that have been merged to main**:
  ```bash
  # List branches to be deleted first for review
  echo "Local branches to be deleted:"
  git branch --merged main | grep -v "^\*\|main\|master\|develop"
  
  # Then delete them after confirmation
  git branch --merged main | grep -v "^\*\|main\|master\|develop" | xargs -n 1 git branch -d
  ```

- **Find and clean up remote branches that have been merged to main**:
  ```bash
  # List branches to be deleted first for review
  echo "Remote branches to be deleted:"
  git branch -r --merged main | grep -v "^\*\|main\|master\|develop" | sed 's/origin\///'
  
  # Then delete them after confirmation
  git branch -r --merged main | grep -v "^\*\|main\|master\|develop" | sed 's/origin\///' | xargs -I{} git push origin --delete {}
  ```

- **Prune local references to deleted remote branches**:
  ```bash
  git remote prune origin
  ```

- **Clean up stale local branches (based on age)**:
  ```bash
  # List branches older than 3 months for review
  echo "Stale branches (older than 3 months):"
  git branch --format "%(refname:short) %(committerdate:relative)" | grep "months ago" | cut -d' ' -f1
  ```

## 3. Working Directory Cleanup

- **Remove untracked files and directories**:
  ```bash
  # Dry run first to see what would be deleted
  git clean -n -d
  
  # Then delete after review (use with caution)
  # git clean -fd
  ```

- **Remove ignored files too (optional)**:
  ```bash
  # Include files specified in .gitignore
  # git clean -fdx
  ```

- **Check for large files in git history**:
  ```bash
  # Find the 10 largest files in git history
  git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print substr($0,6)}' | sort -k2nr | head -n 10
  ```

- **Remove build artifacts and temporary files**:
  ```bash
  # Remove common build directories
  rm -rf dist build .cache coverage
  
  # Remove log files
  find . -name "*.log" -type f -delete
  
  # Remove temporary files
  find . -name "*.tmp" -type f -delete
  ```

# COMPREHENSIVE MAINTENANCE TASKS

## 1. Dependency Management

### Principles:
- Keep dependencies updated but stable
- Follow semantic versioning for updates
- Document all dependency changes
- Regularly audit for security vulnerabilities

### Actions:

- **Audit dependencies for security issues**:
  ```bash
  npm audit
  ```

- **Clean pnpm cache to recover disk space**:
  ```bash
  npm cache clean --force
  ```

- **Check for outdated dependencies**:
  ```bash
  npm outdated
  
  # Generate a report of outdated dependencies
  npm outdated --format json > outdated-deps-$(date +%Y%m%d).json
  ```

- **Update dependencies strategically**:
  ```bash
  # Update patch versions (safest)
  npm update
  
  # Test after each significant update
  npm test
  ```

- **Clean reinstall when needed**:
  ```bash
  rm -rf node_modules
  npm install
  ```

- **Check for duplicate dependencies**:
  ```bash
  npm dedupe
  ```

## 2. Code Quality Maintenance

### Principles:
- Maintain consistent code style
- Eliminate dead code regularly
- Keep test coverage high
- Document code changes and decisions

### Actions:

- **Run comprehensive code quality checks**:
  ```bash
  # Run linting
  npm run lint
  
  # Run formatting
  npm run format
  
  # Fix auto-fixable issues
  npm run lint:fix
  ```

- **Run tests to ensure everything works**:
  ```bash
  # Run unit tests
  npm run test
  
  # Run with coverage report
  npm run test:coverage
  
  # Run end-to-end tests if available
  npm run test:e2e
  ```

- **Find unused dependencies**:
  ```bash
  npx depcheck
  ```

- **Find unused code and dead code paths**:
  ```bash
  # Using ESLint plugin if configured
  npm run lint -- --rule 'no-unused-vars: error'
  ```

## 3. Git Repository Optimization

### Principles:
- Keep repository size manageable
- Maintain clean history
- Optimize for performance
- Preserve data integrity

### Actions:

- **Garbage collection to optimize repository**:
  ```bash
  # Standard garbage collection
  git gc
  
  # More aggressive optimization (takes longer)
  git gc --aggressive
  ```

- **Verify repository integrity**:
  ```bash
  git fsck --full
  ```

- **Check repository size and composition**:
  ```bash
  git count-objects -v -H
  ```

- **Compact and optimize repository**:
  ```bash
  # Repack the repository
  git repack -a -d -f
  ```

- **Find large files in history**:
  ```bash
  # Requires git-filter-repo tool
  git filter-repo --analyze
  ```

## 4. Documentation Maintenance

### Principles:
- Keep documentation in sync with code
- Document maintenance procedures
- Update changelogs and release notes
- Maintain clear architecture documentation

### Actions:

- **Update README and documentation**:
  ```bash
  # Check for outdated documentation
  find docs -type f -name "*.md" -mtime +90 | sort
  ```

- **Update changelog**:
  ```bash
  # Generate changelog from git history
  git log --pretty=format:"%h - %s (%an, %ar)" --since="last month" > RECENT_CHANGES.md
  ```

- **Document maintenance performed**:
  ```bash
  echo "Repository maintenance performed on $(date)" >> MAINTENANCE_LOG.md
  ```

## 5. Performance Optimization

### Principles:
- Regularly measure and improve performance
- Identify and fix bottlenecks
- Monitor resource usage
- Document performance changes

### Actions:

- **Run performance tests if available**:
  ```bash
  # If you have performance tests
  npm run test:performance
  ```

- **Check bundle sizes**:
  ```bash
  # If using webpack bundle analyzer or similar
  npm run analyze-bundle
  ```

# AUTOMATION & CONTINUOUS MAINTENANCE

## Principles:
- Automate routine maintenance
- Schedule regular cleanup tasks
- Monitor repository health
- Integrate maintenance into workflow

## Actions:

- **Create a maintenance script**:
  ```bash
  # Create a script to automate routine maintenance
  cat > scripts/maintenance.sh << 'EOF'
  #!/bin/bash
  echo "Running repository maintenance $(date)";
  git fetch --all --prune;
  git checkout main;
  git pull;
  echo "Cleaning merged branches...";
  git branch --merged main | grep -v "^\*\|main\|master\|develop" | xargs -n 1 git branch -d;
  echo "Running tests...";
  npm test;
  echo "Maintenance complete!";
  EOF
  
  chmod +x scripts/maintenance.sh
  ```

- **Set up git hooks for maintenance**:
  ```bash
  # Create a post-merge hook to clean up after pulls/merges
  mkdir -p .git/hooks
  cat > .git/hooks/post-merge << 'EOF'
  #!/bin/bash
  echo "Running post-merge maintenance...";
  git remote prune origin;
  npm install;
  EOF
  
  chmod +x .git/hooks/post-merge
  ```

- **Add maintenance to CI/CD pipeline**:
  ```bash
  # Example GitHub Action workflow - save to .github/workflows/maintenance.yml
  cat > .github/workflows/maintenance.yml << 'EOF'
  name: Repository Maintenance
  on:
    schedule:
      - cron: '0 0 * * 0'  # Weekly on Sunday
  jobs:
    maintenance:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Setup Node.js
          uses: actions/setup-node@v3
        - name: Install dependencies
          run: npm install
        - name: Run maintenance tasks
          run: |
            git fetch --all --prune
            npm outdated
            npm audit
  EOF
  ```

# VERIFICATION & COMPLETION

## Principles:
- Always verify after maintenance
- Document what was done
- Communicate changes to team
- Learn and improve process

## Actions:

- **Verify repository status**:
  ```bash
  git status
  ```

- **Compare before and after state**:
  ```bash
  # Compare branch list before and after
  git branch -a > branch-list-after-cleanup.txt
  diff branch-list-before-cleanup.txt branch-list-after-cleanup.txt
  ```

- **Run full test suite**:
  ```bash
  npm run test
  ```

- **Document maintenance performed**:
  ```bash
  cat > MAINTENANCE_REPORT.md << EOF
  # Maintenance Report - $(date +%Y-%m-%d)
  
  ## Actions Performed
  - Cleaned up merged branches
  - Updated dependencies
  - Optimized repository size
  - Ran code quality checks
  
  ## Results
  - Removed $(wc -l < branch-list-before-cleanup.txt) - $(wc -l < branch-list-after-cleanup.txt) branches
  - Repository size: $(git count-objects -v -H | grep 'size-pack')
  - All tests passing: $(npm run test > /dev/null && echo "Yes" || echo "No")
  
  ## Next Steps
  - Schedule next maintenance for $(date -d "+30 days" +%Y-%m-%d)
  - Address any issues found during maintenance
  EOF
  ```

- **Communicate with team**:
  ```bash
  # If using GitHub, create an issue with the maintenance report
  gh issue create --title "Maintenance Report $(date +%Y-%m-%d)" --body-file MAINTENANCE_REPORT.md --label "maintenance"
  ```

# MAINTENANCE BEST PRACTICES SUMMARY

1. **Regular Schedule**: Establish a consistent maintenance schedule
2. **Incremental Changes**: Make small, frequent cleanups rather than infrequent large ones
3. **Documentation**: Keep records of all maintenance activities
4. **Automation**: Automate as much of the maintenance process as possible
5. **Testing**: Always test before and after maintenance
6. **Communication**: Keep the team informed about maintenance activities
7. **Backup**: Always create backups before major maintenance
8. **Review**: Regularly review and improve maintenance processes
9. **Integration**: Make maintenance part of the development workflow
10. **Education**: Ensure all team members understand maintenance practices

Remember that repository maintenance is not just about cleaning up; it's about establishing sustainable practices that keep your codebase healthy and your team productive over the long term.
