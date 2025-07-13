Generate CHANGELOG.md from git commit history for WeNexus: $ARGUMENTS.

This command supports multiple modes:
- **Full changelog**: Generate changelog from all commits since last tag
- **PR changelog**: Generate changelog for the latest merged PR only
- **Range changelog**: Generate changelog for specific commit range

# USAGE MODES

## Mode 1: Latest PR Changelog
```bash
claude generate-changelog --pr
claude generate-changelog --latest-pr
```

## Mode 2: Full Version Changelog  
```bash
claude generate-changelog
claude generate-changelog --full
```

## Mode 3: Custom Range Changelog
```bash
claude generate-changelog --range v1.0.0..HEAD
claude generate-changelog --since v1.0.0
```

# PLAN

1. **Determine changelog scope** (PR, full, or range)
2. **Analyze commit history** and identify relevant commits
3. **Parse conventional commits** to categorize changes
4. **Generate structured changelog** with proper formatting
5. **Update existing CHANGELOG.md** or create new one
6. **Validate and commit** the changelog updates

# PREREQUISITES

- Ensure you're on the main branch with latest changes:
  ```bash
  git checkout main
  git pull origin main
  ```

- Verify git history is available:
  ```bash
  git log --oneline -10
  ```

# CHANGELOG GENERATION

## Step 1: Determine Scope and Get Commits

Use TodoWrite tool to track progress, then determine which commits to include:

### For Latest PR Mode (--pr or --latest-pr):
```bash
# Find the most recent merged PR
LATEST_PR=$(gh pr list --state merged --limit 1 --json number --jq '.[0].number')
echo "Latest merged PR: #$LATEST_PR"

# Get PR details
gh pr view $LATEST_PR --json title,headRefName,baseRefName,mergeCommit

# Get commit range for the PR (from merge base to merge commit)
MERGE_COMMIT=$(gh pr view $LATEST_PR --json mergeCommit --jq '.mergeCommit.oid')
BASE_BRANCH=$(gh pr view $LATEST_PR --json baseRefName --jq '.baseRefName')
PR_BRANCH=$(gh pr view $LATEST_PR --json headRefName --jq '.headRefName')

# Find merge base and get PR commits
MERGE_BASE=$(git merge-base origin/$BASE_BRANCH $MERGE_COMMIT)
COMMIT_RANGE="$MERGE_BASE..$MERGE_COMMIT"

echo "PR commit range: $COMMIT_RANGE"
echo "Commits in PR #$LATEST_PR:"
git log $COMMIT_RANGE --oneline --pretty=format:"%h %s"
```

### For Full Version Mode (default or --full):
```bash
# Get latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
echo "Latest tag: $LATEST_TAG"

# Get commits since last tag (or all commits if no tags)
if [ -n "$LATEST_TAG" ]; then
  COMMIT_RANGE="$LATEST_TAG..HEAD"
  git log $COMMIT_RANGE --oneline --pretty=format:"%h %s"
else
  COMMIT_RANGE="HEAD~50..HEAD"
  git log $COMMIT_RANGE --oneline --pretty=format:"%h %s"
fi
```

### For Custom Range Mode (--range or --since):
```bash
# Use provided range from arguments
COMMIT_RANGE="$PROVIDED_RANGE"  # e.g., "v1.0.0..HEAD"
echo "Custom range: $COMMIT_RANGE"
git log $COMMIT_RANGE --oneline --pretty=format:"%h %s"
```

## Step 2: Parse Conventional Commits

Use TodoWrite tool to track changelog generation progress, then analyze commits by type:

### Commit Categories:
- **Features** (`feat:`) - New functionality
- **Bug Fixes** (`fix:`) - Bug fixes
- **Documentation** (`docs:`) - Documentation changes
- **Styles** (`style:`) - Code style changes
- **Refactoring** (`refactor:`) - Code refactoring
- **Performance** (`perf:`) - Performance improvements
- **Tests** (`test:`) - Test additions/changes
- **Build** (`build:`) - Build system changes
- **CI** (`ci:`) - CI configuration changes
- **Chores** (`chore:`) - Other changes

### Parse and categorize commits:
```bash
# Create temporary files for each category
feat_commits=$(mktemp)
fix_commits=$(mktemp)
docs_commits=$(mktemp)
style_commits=$(mktemp)
refactor_commits=$(mktemp)
perf_commits=$(mktemp)
test_commits=$(mktemp)
build_commits=$(mktemp)
ci_commits=$(mktemp)
chore_commits=$(mktemp)
breaking_commits=$(mktemp)
other_commits=$(mktemp)

echo "Parsing commits in range: $COMMIT_RANGE"

# Extract commits by type with improved parsing
git log $COMMIT_RANGE --oneline --pretty=format:"%h %s" | while IFS=' ' read -r hash subject; do
  # Check for breaking changes first
  if echo "$subject" | grep -E "(BREAKING CHANGE|!:|!)" >/dev/null; then
    echo "- $subject ($hash)" >> $breaking_commits
  fi
  
  # Categorize by conventional commit type
  case "$subject" in
    feat:*|feat\(*\):*) echo "- ${subject#feat*: } ($hash)" >> $feat_commits ;;
    fix:*|fix\(*\):*) echo "- ${subject#fix*: } ($hash)" >> $fix_commits ;;
    docs:*|docs\(*\):*) echo "- ${subject#docs*: } ($hash)" >> $docs_commits ;;
    style:*|style\(*\):*) echo "- ${subject#style*: } ($hash)" >> $style_commits ;;
    refactor:*|refactor\(*\):*) echo "- ${subject#refactor*: } ($hash)" >> $refactor_commits ;;
    perf:*|perf\(*\):*) echo "- ${subject#perf*: } ($hash)" >> $perf_commits ;;
    test:*|test\(*\):*) echo "- ${subject#test*: } ($hash)" >> $test_commits ;;
    build:*|build\(*\):*) echo "- ${subject#build*: } ($hash)" >> $build_commits ;;
    ci:*|ci\(*\):*) echo "- ${subject#ci*: } ($hash)" >> $ci_commits ;;
    chore:*|chore\(*\):*) echo "- ${subject#chore*: } ($hash)" >> $chore_commits ;;
    *) echo "- $subject ($hash)" >> $other_commits ;;
  esac
done

# Show parsing results
echo "Found $(wc -l < $feat_commits) feature commits"
echo "Found $(wc -l < $fix_commits) fix commits"
echo "Found $(wc -l < $breaking_commits) breaking change commits"
```

## Step 3: Generate Changelog Entry

### Determine entry type and title:
```bash
# Get current date
CURRENT_DATE=$(date +"%Y-%m-%d")

# Determine title based on mode
if [[ "$*" == *"--pr"* ]] || [[ "$*" == *"--latest-pr"* ]]; then
  # For PR mode, use PR title and number
  PR_TITLE=$(gh pr view $LATEST_PR --json title --jq '.title')
  ENTRY_TITLE="PR #$LATEST_PR: $PR_TITLE"
  VERSION="PR-$LATEST_PR"
else
  # For version mode, get version from package.json
  if [ -f "package.json" ]; then
    VERSION=$(grep '"version"' package.json | sed 's/.*"version": "\(.*\)".*/\1/')
  else
    VERSION="Unreleased"
  fi
  ENTRY_TITLE="$VERSION"
fi

echo "Generating changelog entry: $ENTRY_TITLE"
echo "Date: $CURRENT_DATE"
```

### Build changelog entry:
```bash
# Start building changelog entry
if [[ "$*" == *"--pr"* ]] || [[ "$*" == *"--latest-pr"* ]]; then
  # PR-specific format
  CHANGELOG_ENTRY="## [$ENTRY_TITLE] - $CURRENT_DATE\n\n"
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}**Pull Request:** [#$LATEST_PR](https://github.com/$(gh repo view --json owner,name --jq '.owner.login + \"/\" + .name')/pull/$LATEST_PR)\n"
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}**Branch:** $PR_BRANCH → $BASE_BRANCH\n\n"
else
  # Version release format
  CHANGELOG_ENTRY="## [$VERSION] - $CURRENT_DATE\n\n"
fi

# Add breaking changes first (if any)
if [ -s $breaking_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### ⚠️ BREAKING CHANGES\n$(cat $breaking_commits)\n\n"
fi

# Add sections only if they have content
if [ -s $feat_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### ✨ Added\n$(cat $feat_commits)\n\n"
fi

if [ -s $fix_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 🐛 Fixed\n$(cat $fix_commits)\n\n"
fi

if [ -s $refactor_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 🔄 Changed\n$(cat $refactor_commits)\n\n"
fi

if [ -s $perf_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### ⚡ Performance\n$(cat $perf_commits)\n\n"
fi

if [ -s $docs_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 📚 Documentation\n$(cat $docs_commits)\n\n"
fi

if [ -s $test_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 🧪 Tests\n$(cat $test_commits)\n\n"
fi

if [ -s $build_commits ] || [ -s $ci_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 🏗️ Build & CI\n"
  [ -s $build_commits ] && CHANGELOG_ENTRY="${CHANGELOG_ENTRY}$(cat $build_commits)\n"
  [ -s $ci_commits ] && CHANGELOG_ENTRY="${CHANGELOG_ENTRY}$(cat $ci_commits)\n"
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}\n"
fi

if [ -s $style_commits ] || [ -s $chore_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 🧹 Maintenance\n"
  [ -s $style_commits ] && CHANGELOG_ENTRY="${CHANGELOG_ENTRY}$(cat $style_commits)\n"
  [ -s $chore_commits ] && CHANGELOG_ENTRY="${CHANGELOG_ENTRY}$(cat $chore_commits)\n"
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}\n"
fi

if [ -s $other_commits ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}### 📝 Other\n$(cat $other_commits)\n\n"
fi

# Clean up temp files
rm -f $feat_commits $fix_commits $docs_commits $style_commits $refactor_commits $perf_commits $test_commits $build_commits $ci_commits $chore_commits $breaking_commits $other_commits

echo "Generated changelog entry with $(echo -e "$CHANGELOG_ENTRY" | wc -l) lines"
```

## Step 4: Update CHANGELOG.md

### Use the Edit tool to update CHANGELOG.md:

1. **Read existing CHANGELOG.md** to understand current structure
2. **Insert new entry** in the appropriate location:
   - For PR entries: Add after `## [Unreleased]` section  
   - For version entries: Replace `## [Unreleased]` or add after it
3. **Preserve existing formatting** and structure

### Alternative bash approach:
```bash
if [ -f "CHANGELOG.md" ]; then
  # Create backup
  cp CHANGELOG.md CHANGELOG.md.backup
  
  # Insert new entry after "## [Unreleased]" section
  if [[ "$*" == *"--pr"* ]] || [[ "$*" == *"--latest-pr"* ]]; then
    # For PR entries, add after Unreleased
    sed -i "/## \[Unreleased\]/a\\
\\
$CHANGELOG_ENTRY" CHANGELOG.md
  else
    # For version entries, replace or add after Unreleased
    if grep -q "## \[Unreleased\]" CHANGELOG.md; then
      sed -i "/## \[Unreleased\]/a\\
\\
$CHANGELOG_ENTRY" CHANGELOG.md
    else
      # Insert at beginning after header
      sed -i "3a\\
\\
$CHANGELOG_ENTRY" CHANGELOG.md
    fi
  fi
else
  # Create new CHANGELOG.md
  cat > CHANGELOG.md << EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

$CHANGELOG_ENTRY
EOF
fi

echo "CHANGELOG.md updated successfully"
```

## Step 5: Review and Validate

### Manual review:
```bash
# Show the changes
git diff CHANGELOG.md

# View the updated changelog  
head -50 CHANGELOG.md

# Validate the entry
echo -e "$CHANGELOG_ENTRY" | head -20
```

### Validation checklist:
- [ ] Changelog follows Keep a Changelog format
- [ ] All significant changes are included
- [ ] Commit hashes are included for traceability
- [ ] Version/PR number and date are correct
- [ ] Categories are properly organized with emojis
- [ ] No duplicate entries
- [ ] Breaking changes are highlighted at the top
- [ ] PR links are working (for PR mode)

## Step 6: Commit Changes

```bash
# Stage the changelog
git add CHANGELOG.md

# Create appropriate commit message
if [[ "$*" == *"--pr"* ]] || [[ "$*" == *"--latest-pr"* ]]; then
  COMMIT_MSG="docs: add changelog entry for PR #$LATEST_PR

- Document changes from $PR_TITLE
- Include all commits from the pull request
- Follow Keep a Changelog format

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>

References #$LATEST_PR"
else
  COMMIT_MSG="docs: update CHANGELOG.md for version $VERSION

- Add changelog entries from commit history
- Include all changes since last release
- Follow Keep a Changelog format

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi

# Commit the changes
git commit -m "$COMMIT_MSG"

# Optional: Create a tag for version releases
if [[ "$VERSION" != "Unreleased" ]] && [[ "$VERSION" != PR-* ]]; then
  read -p "Create tag v$VERSION? (y/N): " create_tag
  if [[ "$create_tag" =~ ^[Yy]$ ]]; then
    git tag -a "v$VERSION" -m "Release version $VERSION"
    echo "Created tag: v$VERSION"
  fi
fi
```

# USAGE EXAMPLES

## Generate changelog for latest merged PR:
```bash
claude generate-changelog --pr
claude generate-changelog --latest-pr  
```

## Generate full version changelog:
```bash
claude generate-changelog
claude generate-changelog --full
```

## Generate changelog for specific range:
```bash
claude generate-changelog --range v1.0.0..HEAD
claude generate-changelog --since v1.0.0
```

# ADVANCED FEATURES

## PR Analysis with Details
```bash
# Get detailed PR information
gh pr view $LATEST_PR --json title,body,author,reviewers,labels --jq '{
  title: .title,
  author: .author.login,
  reviewers: [.reviewers[].login],
  labels: [.labels[].name]
}'

# Include reviewer acknowledgments in changelog
REVIEWERS=$(gh pr view $LATEST_PR --json reviewers --jq '[.reviewers[].login] | join(", ")')
if [ -n "$REVIEWERS" ]; then
  CHANGELOG_ENTRY="${CHANGELOG_ENTRY}**Reviewed by:** $REVIEWERS\n\n"
fi
```

## Include Breaking Change Details
```bash
# Extract breaking change details from commit bodies
git log $COMMIT_RANGE --grep="BREAKING CHANGE:" --pretty=format:"%B" | 
  sed -n '/BREAKING CHANGE:/,/^$/p' | 
  sed 's/BREAKING CHANGE://' | 
  sed '/^$/d' | 
  sed 's/^/- /'
```

## Generate Release Notes for GitHub
```bash
# Create GitHub release notes format
cat > RELEASE_NOTES.md << EOF
# 🚀 $ENTRY_TITLE

$(echo -e "$CHANGELOG_ENTRY" | sed 's/^## \[.*\] - .*$//' | sed '/^$/d')

---

**Full Changelog**: https://github.com/$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')/compare/$PREVIOUS_TAG...v$VERSION
EOF
```

# BEST PRACTICES

- **Use conventional commits** for accurate parsing
- **Include scope in commits** for better categorization  
- **Mark breaking changes** with `!` or `BREAKING CHANGE:`
- **Review generated changelog** before committing
- **Use PR mode** for documenting individual feature deliveries
- **Use version mode** for release documentation
- **Keep unreleased section** for ongoing development tracking
- **Include emoji categories** for visual clarity

# TROUBLESHOOTING

## No PRs found:
- Check if you're in the right repository
- Verify GitHub CLI authentication: `gh auth status`
- Ensure PRs exist: `gh pr list --state merged`

## No commits in range:
- Verify the commit range is correct
- Check if you're on the right branch
- Ensure git history exists

## GitHub CLI issues:
- Update GitHub CLI: `gh --version` and update if needed
- Re-authenticate: `gh auth login`
- Check repository access: `gh repo view`

## Conventional commit parsing issues:
- Review recent commits for proper format
- Consider manual categorization for non-conventional commits
- Update parsing regex for project-specific patterns

Remember to use the TodoWrite tool to track your progress through each step of the changelog generation process.