# GitHub Rulesets Configuration for Smart Merge Strategy

## Overview
This document provides step-by-step instructions to configure GitHub Rulesets that enforce specific merge strategies based on branch patterns, implementing Method C for Smart Merge Strategy.

## Ruleset Configuration

### Access GitHub Rulesets
1. Navigate to your repository on GitHub
2. Go to **Settings** → **Rules** → **Rulesets**
3. Click **New ruleset** → **New branch ruleset**

### Ruleset 0: Branch Creation Restrictions
**Name**: `Branch Creation Restrictions`
**Priority**: Highest (this should be the first ruleset created)

**Target branches**:
- Include by pattern: `**` (all branches)

**Rules to enable**:
- ✅ **Restrict creations**
  - This blocks creation of ALL branches by default
  - Only branches matching the bypass patterns below will be allowed

**Bypass permissions**: 
- Allow repository admins to bypass (for emergency situations)
- Allow specific patterns to bypass the creation restriction:
  - `feature/**`
  - `fix/**`
  - `chore/**`
  - `main`

**Configuration Notes**:
- This ruleset uses the "restrict by default, allow exceptions" approach
- Any branch name NOT matching `feature/*`, `fix/*`, or `chore/*` will be blocked
- Branch creation attempts with invalid names will show an error message
- This works in combination with the merge strategy rulesets below

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

| Branch Pattern | Creation Allowed | Merge Method | Reasoning |
|---------------|-----------------|--------------|-----------|
| `feature/**` | ✅ **Allowed** | **Squash Merge** | Clean history, group related commits |
| `fix/**` | ✅ **Allowed** | **Merge Commit** | Preserve fix context and audit trail |
| `chore/**` | ✅ **Allowed** | **Squash Merge** | Clean history for maintenance tasks |
| `main` | ✅ **Allowed** | **Protected** | No direct pushes allowed |
| `*` (all others) | ❌ **Blocked** | N/A | Only standard naming conventions allowed |

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
1. Create each ruleset following the configurations above
2. Apply in order: **Branch Creation Restrictions** → Main → Feature → Fix → Chore
3. Test with a sample branch of each type

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