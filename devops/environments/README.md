# GitHub Environment Configuration

This document describes how to set up GitHub environments for manual approval gates.

## File Structure
- DevOps documentation and setup guides are in `/devops/`
- Source code and Databricks assets are in `/src/`
- GitHub Actions workflows are in `.github/workflows/` (GitHub requirement)

## Required Environments

You need to create the following environments in your GitHub repository settings:

### 1. dev Environment
- **Name**: `dev`
- **Protection Rules**: None (automatic deployment)
- **Required Secrets**:
  - `DATABRICKS_DEV_HOST`: Your development Databricks workspace URL
  - `DATABRICKS_DEV_TOKEN`: Personal access token or service principal token for dev

### 2. test Environment  
- **Name**: `test`
- **Protection Rules**: 
  - ✅ Required reviewers (at least 1 reviewer)
  - ✅ Wait timer: 0 minutes
- **Required Secrets**:
  - `DATABRICKS_TEST_HOST`: Your test Databricks workspace URL
  - `DATABRICKS_TEST_TOKEN`: Personal access token or service principal token for test

### 3. prod Environment
- **Name**: `prod` 
- **Protection Rules**:
  - ✅ Required reviewers (at least 2 reviewers)
  - ✅ Wait timer: 5 minutes
  - ✅ Restrict to protected branches only
- **Required Secrets**:
  - `DATABRICKS_PROD_HOST`: Your prod Databricks workspace URL
  - `DATABRICKS_PROD_TOKEN`: Personal access token or service principal token for prod

## Setup Instructions

1. Go to your repository Settings → Environments
2. Click "New environment" for each environment above
3. Configure protection rules as specified
4. Add the required secrets to each environment
5. Add reviewers for test and prod environments

## Deployment Flow

```
PR (feature/*, fix/*, chore/*) → main
                ↓
            Deploy to dev (automatic)
                ↓
         Merge to main branch
                ↓
    Deploy to test (requires 1 approval)
                ↓
   Deploy to prod (requires 2 approvals + 5min wait)
```