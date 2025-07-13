# GitHub Rulesets Configuration for Smart Merge Strategy

## Overview
This document provides step-by-step instructions to configure GitHub Rulesets that enforce specific merge strategies based on branch patterns, implementing Method C for Smart Merge Strategy.

## Ruleset Configuration

### Access GitHub Rulesets
1. Navigate to your repository on GitHub
2. Go to **Settings** → **Rules** → **Rulesets**
3. Click **New ruleset** → **New branch ruleset**

## ⚠️ Important Note About Branch Creation Restrictions

**GitHub Limitation**: Unfortunately, GitHub Rulesets don't currently support pattern-based exclusions for creation restrictions. The "Restrict creations" rule applies to ALL matching branches without the ability to exclude specific patterns.

**Alternative Approaches**:

### Option 1: Use Multiple Targeted Rulesets (Recommended)
Instead of blocking all and allowing exceptions, create specific rules for unwanted patterns:

#### Ruleset 0a: Block Common Invalid Patterns
**Name**: `Block Invalid Branch Patterns`
**Target branches**: 
- `develop`
- `develop/**`
- `bugfix/**` 
- `hotfix/**`
- `release/**`

**Rules**: ✅ **Restrict creations**

#### Ruleset 0b: Block Single Word Branches  
**Name**: `Block Single Word Branches`
**Target branches**: `*` (single level, no slashes)
**Rules**: ✅ **Restrict creations**

### Option 2: Branch Protection Rules (Legacy Method)
Use the older branch protection system to create naming-based restrictions:

#### Steps to Configure:
1. Navigate to your repository **Settings**
2. In the "Code and automation" sidebar, click **Branches**  
3. Click **Add rule**
4. Configure patterns to block unwanted naming:

**Rule 1: Block develop branches**
- Branch name pattern: `develop*`
- ✅ Enable "Restrict pushes that create matching branches"
- In permissions, add only repository admins (blocks everyone else)

**Rule 2: Block single-word branches**  
- Branch name pattern: `*` (no slashes)
- ✅ Enable "Restrict pushes that create matching branches"
- In permissions, add only repository admins

**Rule 3: Block other patterns**
- Branch name pattern: `bugfix*` 
- Branch name pattern: `hotfix*`
- Branch name pattern: `release*`
- ✅ Enable "Restrict pushes that create matching branches"

#### Limitations:
- Requires separate rules for each unwanted pattern
- Uses `fnmatch` syntax (limited pattern matching)
- Cannot create "allow only these patterns" rules directly
- May conflict with newer Rulesets if both are enabled

### Option 3: CI/CD Enforcement (Fallback)
If rulesets are insufficient, use the branch cleanup workflow to detect and flag incorrectly named branches.

### Ruleset 1: Feature Branch Rules
**Name**: `Feature Branch Merge Strategy`

**Target branches**:
- Include by pattern: `feature/**`

**Rules to enable**:
- ✅ **Restrict pushes that create files**
- ✅ **Require a pull request before merging**
  - Required approvals: `1`
  - Dismiss stale reviews when new commits are pushed: `✅`
  - Require review from code owners: `❌` (unless you have CODEOWNERS)
  - Restrict pushes that create files: `❌`
  - Allow specified actors to bypass required pull requests: `❌`

**Advanced Settings**:
- **Merge methods allowed**:
  - ❌ Allow merge commits
  - ✅ Allow squash merging (ENFORCED)
  - ❌ Allow rebase merging
- **Branch protections**:
  - ✅ Require status checks to pass before merging
  - Status checks: Add `validate` (from CI/CD workflow)
  - ✅ Require branches to be up to date before merging

**Bypass permissions**: None (enforce for all users)

### Ruleset 2: Fix Branch Rules  
**Name**: `Fix Branch Merge Strategy`

**Target branches**:
- Include by pattern: `fix/**`

**Rules to enable**:
- ✅ **Restrict pushes that create files**
- ✅ **Require a pull request before merging**
  - Required approvals: `1`
  - Dismiss stale reviews when new commits are pushed: `✅`
  - Require review from code owners: `❌`
  - Allow specified actors to bypass required pull requests: `❌`

**Advanced Settings**:
- **Merge methods allowed**:
  - ✅ Allow merge commits (ENFORCED for audit trail)
  - ❌ Allow squash merging
  - ❌ Allow rebase merging
- **Branch protections**:
  - ✅ Require status checks to pass before merging
  - Status checks: Add `validate` (from CI/CD workflow)  
  - ✅ Require branches to be up to date before merging

**Bypass permissions**: Allow repository admins to bypass (for emergency fixes)

### Ruleset 3: Chore Branch Rules
**Name**: `Chore Branch Merge Strategy`

**Target branches**:
- Include by pattern: `chore/**`

**Rules to enable**:
- ✅ **Restrict pushes that create files**
- ✅ **Require a pull request before merging**
  - Required approvals: `1`
  - Dismiss stale reviews when new commits are pushed: `✅`
  - Require review from code owners: `❌`
  - Allow specified actors to bypass required pull requests: `❌`

**Advanced Settings**:
- **Merge methods allowed**:
  - ❌ Allow merge commits
  - ✅ Allow squash merging (ENFORCED)
  - ❌ Allow rebase merging
- **Branch protections**:
  - ✅ Require status checks to pass before merging
  - Status checks: Add `validate` (from CI/CD workflow)
  - ✅ Require branches to be up to date before merging

**Bypass permissions**: None (enforce for all users)

### Ruleset 4: Main Branch Protection
**Name**: `Main Branch Protection`

**Target branches**:
- Include by pattern: `main`

**Rules to enable**:
- ✅ **Restrict pushes**
  - Only allow pushes through pull requests: `✅`
- ✅ **Require a pull request before merging**
  - Required approvals: `2`
  - Dismiss stale reviews when new commits are pushed: `✅`
  - Require review from code owners: `✅` (if CODEOWNERS exists)
  - Allow specified actors to bypass required pull requests: `❌`

**Advanced Settings**:
- **Branch protections**:
  - ✅ Require status checks to pass before merging
  - Status checks: Add `validate`, `deploy-dev` (from CI/CD workflow)
  - ✅ Require branches to be up to date before merging
  - ✅ Restrict pushes that create files
  - ✅ Block force pushes

**Bypass permissions**: Allow repository admins only (for emergencies)

## Merge Strategy Logic

### Branch Pattern → Rules Mapping

| Branch Pattern | Creation Status | Merge Method | Reasoning |
|---------------|----------------|--------------|-----------|
| `feature/**` | ✅ **Allowed** | **Squash Merge** | Clean history, group related commits |
| `fix/**` | ✅ **Allowed** | **Merge Commit** | Preserve fix context and audit trail |
| `chore/**` | ✅ **Allowed** | **Squash Merge** | Clean history for maintenance tasks |
| `main` | ✅ **Allowed** | **Protected** | No direct pushes allowed |
| `develop/**` | ❌ **Blocked** (Option 1) | N/A | Enforce standard naming |
| `bugfix/**` | ❌ **Blocked** (Option 1) | N/A | Use `fix/` instead |
| `hotfix/**` | ❌ **Blocked** (Option 1) | N/A | Use `fix/` instead |
| Single words | ❌ **Blocked** (Option 1) | N/A | Require descriptive names |

### Rationale

**Feature Branches (`feature/**`) → Squash Merge**:
- Condenses multiple development commits into a single, clean commit
- Maintains readable main branch history
- Groups related feature work together
- Easier to revert entire features if needed

**Fix Branches (`fix/**`) → Merge Commit**:
- Preserves the complete context of the fix
- Maintains audit trail for debugging and compliance
- Shows exactly what changed and when for critical fixes
- Easier to trace hotfixes and emergency patches

**Chore Branches (`chore/**`) → Squash Merge**:
- Cleanup tasks don't need detailed commit history
- Reduces noise in main branch timeline
- Groups related maintenance work together

## Implementation Steps

### Step 1: Create Rulesets
**For Option 1 (Recommended)**:
1. Create the invalid pattern blocking rulesets first
2. Create merge strategy rulesets: Main → Feature → Fix → Chore  
3. Test with valid and invalid branch patterns

**For Option 3 (CI/CD Enforcement)**:
1. Create only the merge strategy rulesets
2. Rely on branch cleanup workflow to detect invalid patterns
3. Use PR reviews to catch naming violations

### Step 2: Validate Configuration
Create test branches to verify both creation restrictions and merge strategy rules:

**Valid Branch Creation (should succeed):**
```bash
# Test feature branch
git checkout -b feature/test-merge-strategy
git push -u origin feature/test-merge-strategy

# Test fix branch  
git checkout -b fix/test-merge-strategy
git push -u origin fix/test-merge-strategy

# Test chore branch
git checkout -b chore/test-merge-strategy  
git push -u origin chore/test-merge-strategy
```

**Invalid Branch Creation (should fail):**
```bash
# These should be blocked by the creation restriction
git checkout -b develop/test-branch      # ❌ Should fail
git checkout -b bugfix/test-branch       # ❌ Should fail  
git checkout -b hotfix/test-branch       # ❌ Should fail
git checkout -b random-branch-name       # ❌ Should fail
```

### Step 3: Team Communication
1. Inform team about new merge strategy rules
2. Document branch naming conventions
3. Provide training on when to use each branch type

## Branch Lifecycle Integration

This merge strategy works with the branch cleanup workflow:

1. **Branch Creation**: Follow naming conventions (`feature/`, `fix/`, `chore/`)
2. **Development**: Work within appropriate branch lifespan (3-7 days)
3. **Pull Request**: Automatic enforcement of merge strategy based on branch name
4. **Merge**: GitHub enforces the correct merge method
5. **Cleanup**: Branch cleanup workflow flags stale branches

## Troubleshooting

### Common Issues

**"Branch creation blocked" error**:
- Error message: "Branch creation is restricted by repository rules"
- **Solution**: Ensure branch name follows allowed patterns: `feature/*`, `fix/*`, or `chore/*`
- **Example**: Change `develop/my-feature` to `feature/my-feature`
- Check that the Branch Creation Restrictions ruleset is configured correctly

**"Merge method not allowed" error**:
- Check ruleset configuration for the branch pattern
- Verify branch name matches the expected pattern exactly
- Ensure ruleset is active and properly configured

**Status checks failing**:
- Verify CI/CD workflow names match those specified in rulesets
- Check that required jobs are completing successfully
- Update ruleset status check names if workflow jobs change

**Bypass not working**:
- Check user permissions in repository settings
- Verify bypass permissions are correctly configured in ruleset
- Confirm user has appropriate role (admin/maintain)

**Branch creation works locally but fails on GitHub**:
- Local git doesn't enforce GitHub rulesets - only GitHub's remote repository does
- Branches created locally can still be pushed if they follow naming conventions
- The restriction applies when pushing new branch names to the remote repository

### Monitoring and Maintenance

1. **Regular Review**: Check ruleset effectiveness monthly
2. **Metrics Tracking**: Monitor merge method usage patterns
3. **Team Feedback**: Gather input on workflow efficiency
4. **Rule Updates**: Adjust based on team needs and project evolution

## Advanced Configuration Options

### Additional Rules to Consider

**Branch Naming Enforcement**:
- ✅ **Already implemented** with Branch Creation Restrictions ruleset
- Blocks branches not following `feature/`, `fix/`, `chore/` conventions

**Commit Message Standards**:
- Enforce conventional commit format
- Require specific prefixes or patterns

**File Protection**:
- Protect critical files (CI/CD configs, databricks.yml)
- Require additional approvals for sensitive changes

**Size Limits**:
- Restrict PR size to encourage focused changes
- Set file count or line change limits

## Summary

This configuration implements a comprehensive branch governance system that:

1. **Restricts branch creation** to only `feature/*`, `fix/*`, and `chore/*` patterns
2. **Enforces specific merge strategies** based on branch type
3. **Integrates seamlessly** with existing CI/CD pipeline and branch cleanup workflows
4. **Balances code quality, audit requirements, and development efficiency**

The combination of creation restrictions and merge strategy enforcement ensures consistent, high-quality branch management across the entire development lifecycle.