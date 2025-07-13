# GitHub Rulesets Configuration for Smart Merge Strategy

## Overview
This document provides step-by-step instructions to configure GitHub Rulesets that enforce specific merge strategies based on branch patterns, implementing Method C for Smart Merge Strategy.

## Ruleset Configuration

### Access GitHub Rulesets
1. Navigate to your repository on GitHub
2. Go to **Settings** → **Rules** → **Rulesets**
3. Click **New ruleset** → **New branch ruleset**

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

### Branch Pattern → Merge Method Mapping

| Branch Pattern | Merge Method | Reasoning |
|---------------|--------------|-----------|
| `feature/**` | **Squash Merge** | Clean history, group related commits |
| `fix/**` | **Merge Commit** | Preserve fix context and audit trail |
| `chore/**` | **Squash Merge** | Clean history for maintenance tasks |
| `main` | **Protected** | No direct pushes allowed |

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
2. Apply in order: Main → Feature → Fix → Chore
3. Test with a sample branch of each type

### Step 2: Validate Configuration
Create test branches to verify rules:
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

### Monitoring and Maintenance

1. **Regular Review**: Check ruleset effectiveness monthly
2. **Metrics Tracking**: Monitor merge method usage patterns
3. **Team Feedback**: Gather input on workflow efficiency
4. **Rule Updates**: Adjust based on team needs and project evolution

## Advanced Configuration Options

### Additional Rules to Consider

**Branch Naming Enforcement**:
- Add ruleset to require specific branch naming patterns
- Reject branches not following `feature/`, `fix/`, `chore/` conventions

**Commit Message Standards**:
- Enforce conventional commit format
- Require specific prefixes or patterns

**File Protection**:
- Protect critical files (CI/CD configs, databricks.yml)
- Require additional approvals for sensitive changes

**Size Limits**:
- Restrict PR size to encourage focused changes
- Set file count or line change limits

This configuration implements a robust merge strategy that balances code quality, audit requirements, and development efficiency while integrating seamlessly with the existing CI/CD pipeline and branch management workflows.