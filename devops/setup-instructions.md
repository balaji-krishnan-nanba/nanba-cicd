# Databricks CI/CD Setup Instructions

## Overview
This repository contains a complete CI/CD pipeline for Azure Databricks using Databricks Asset Bundles and GitHub Actions.

## Prerequisites

1. **Azure Databricks Workspaces**
   - Development workspace
   - Test workspace  
   - Production workspace

2. **Databricks CLI Access Tokens**
   - Service principal or personal access tokens for each environment
   - Proper permissions for bundle deployment

3. **GitHub Repository Secrets**
   - Configure environment-specific secrets (see Environment Setup below)

## Quick Start

1. **Clone and Initialize**
   ```bash
   git clone <your-repo>
   cd nanba-cicd
   ```

2. **Install Databricks CLI** (local development)
   ```bash
   curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
   ```

3. **Configure Databricks Bundle**
   - Update `src/databricks.yml` with your workspace URLs
   - Modify resource configurations as needed

4. **Set up GitHub Environments** (see `devops/environments/README.md`)

## Environment Setup

### GitHub Secrets Configuration

#### Repository Level Secrets (optional)
- `DATABRICKS_HOST`: Default host (if using single workspace)
- `DATABRICKS_TOKEN`: Default token (if using single workspace)

#### Environment Specific Secrets

**dev environment:**
- `DATABRICKS_DEV_HOST`: `https://your-dev-workspace.cloud.databricks.com`
- `DATABRICKS_DEV_TOKEN`: Your development access token

**test environment:**
- `DATABRICKS_TEST_HOST`: `https://your-test-workspace.cloud.databricks.com`  
- `DATABRICKS_TEST_TOKEN`: Your test access token

**prod environment:**
- `DATABRICKS_PROD_HOST`: `https://your-prod-workspace.cloud.databricks.com`
- `DATABRICKS_PROD_TOKEN`: Your prod access token

## Workflow Triggers

### Automatic Deployment to Dev
- **Trigger**: PR opened/updated from branches matching:
  - `feature/*`
  - `fix/*` 
  - `chore/*`
- **Target**: `main` branch
- **Environment**: `dev`
- **Approval**: None required

### Automatic Deployment to Test (with Approval)
- **Trigger**: Automatic on push to `main` branch OR manual dispatch
- **Environment**: `test`
- **Approval**: 1 reviewer required (must be approved before deployment)
- **Dependencies**: Successful bundle validation

### Semantic Versioning and Tagging
- **Trigger**: Automatic on push to `main` branch (after test deployment)
- **Process**: Analyzes conventional commits since last release
- **Output**: Creates semantic version tags (v1.0.0, v1.1.0, etc.)
- **Dependencies**: Test deployment completion
- **Documentation**: See `devops/semantic-versioning-guide.md`

### Automatic Prod Deployment
- **Trigger**: Semantic version tag creation (v*.*.*)
- **Environment**: `prod`
- **Approval**: 2 reviewers required + 5 minute wait timer
- **Dependencies**: Successful semantic release
- **Version Info**: Deployment includes Git tag, commit SHA, and version metadata

## Workspace Path Configuration

### Environment-Specific Deployment Paths

This CI/CD pipeline uses different deployment strategies for each environment:

#### **Development Environment**
- **Path**: `/Workspace/Users/${workspace.current_user.userName}/.bundle/nanba-cicd/dev`
- **Strategy**: User-specific paths for development isolation
- **Use Case**: Individual developer testing and experimentation

#### **Test Environment** 
- **Path**: `/Workspace/Shared/.bundle/nanba-cicd/test`
- **Strategy**: Shared workspace location for team collaboration
- **Use Case**: Integration testing and team validation

#### **Prod Environment**
- **Path**: `/Workspace/Shared/.bundle/nanba-cicd/prod`
- **Strategy**: Shared workspace location for prod stability
- **Use Case**: Prod deployments with team access and audit trails

### Best Practices for Prod

1. **Shared Locations**: Test and prod use `/Workspace/Shared/` to avoid dependency on individual user accounts
2. **Service Principals**: Recommended for test/prod authentication instead of personal tokens
3. **Team Access**: Multiple team members can manage and troubleshoot shared deployments
4. **Audit Trail**: Centralized location for better monitoring and compliance
5. **Disaster Recovery**: Reduced single points of failure

## Project Structure

```
├── src/                        # Source code and Databricks assets
│   ├── databricks.yml         # Main bundle configuration
│   ├── resources/
│   │   └── jobs.yml           # Job definitions
│   └── notebooks/
│       ├── validation.py      # Dev environment validation
│       ├── integration_tests.py # Test environment integration tests
│       └── smoke_tests.py     # Production smoke tests
├── devops/                     # CI/CD pipeline configurations
│   ├── environments/
│   │   └── README.md          # Environment setup guide
│   └── setup-instructions.md  # This file
└── .github/                    # GitHub Actions workflows
    └── workflows/
        └── databricks-cicd.yml # CI/CD pipeline workflow
```

## Local Development

### Validate Bundle
```bash
cd src
databricks bundle validate --target dev
```

### Deploy to Development
```bash
cd src
databricks bundle deploy --target dev
```

### Run Jobs
```bash
cd src
databricks bundle run --target dev validation_job
```

## Service Principal Setup (Recommended for Prod)

### Why Use Service Principals?

For test and prod environments, using service principals instead of personal access tokens provides:
- **Security**: Dedicated authentication without personal account dependencies
- **Team Access**: Multiple team members can manage the same service principal
- **Audit Trail**: Clear tracking of automated vs. manual activities
- **Compliance**: Better alignment with enterprise security policies

### Creating Service Principals

#### **Step 1: Create Service Principal in Databricks**
1. Go to your Databricks workspace → **Settings** → **Identity and access** → **Service principals**
2. Click **Add service principal**
3. Name: `nanba-cicd-test-sp` (for test) or `nanba-cicd-prod-sp` (for prod)
4. Click **Add**

#### **Step 2: Generate Client Secret**
1. Click on the created service principal
2. Go to **Secrets** tab
3. Click **Generate secret**
4. **Copy the secret immediately** (you won't see it again!)

#### **Step 3: Assign Permissions**
1. **Workspace Access**: Add service principal to the workspace
2. **Cluster Permissions**: Grant "Can Restart" permissions
3. **Storage Access**: Configure access to data sources if needed
4. **Unity Catalog**: Grant appropriate catalog/schema permissions

#### **Step 4: Update GitHub Secrets**
Replace personal tokens with service principal credentials:

**For Test Environment:**
- `DATABRICKS_TEST_HOST`: Your test workspace URL
- `DATABRICKS_TEST_TOKEN`: Service principal secret

**For Prod Environment:**
- `DATABRICKS_PROD_HOST`: Your prod workspace URL  
- `DATABRICKS_PROD_TOKEN`: Service principal secret

### Service Principal Best Practices

1. **Separate Service Principals**: Use different service principals for test and prod
2. **Minimal Permissions**: Grant only the permissions needed for CI/CD operations
3. **Regular Rotation**: Rotate service principal secrets periodically
4. **Monitoring**: Set up alerts for service principal usage
5. **Documentation**: Document service principal purposes and permissions

## Semantic Versioning and Commit Standards

### Conventional Commits Required
This pipeline uses **conventional commits** to automatically determine version numbers:

- `feat:` → Minor version bump (v1.1.0)
- `fix:` → Patch version bump (v1.0.1)  
- `feat!:` or `BREAKING CHANGE:` → Major version bump (v2.0.0)
- `docs:`, `test:`, `chore:` → No release

### Examples
```bash
feat: add customer data pipeline          # v1.1.0
fix: resolve data validation error        # v1.0.1
feat!: change data schema format          # v2.0.0
docs: update API documentation             # No release
```

### Version-Tagged Deployments
- Prod deployments are **only triggered by semantic version tags**
- Each prod deployment includes version metadata in job names
- Git commit SHA and tag information is embedded in Databricks resources
- Full traceability from code commit to prod deployment

For complete guidelines, see [`devops/semantic-versioning-guide.md`](semantic-versioning-guide.md).

### Commit Message Enforcement
A **commitlint workflow** automatically validates all commit messages:
- ✅ Valid: `feat: add data pipeline`, `fix: resolve validation error`
- ❌ Invalid: `updated code`, `bug fix`, `changes`

**Failed commits will block PR merges** when branch protection is enabled.

## Branch Protection Setup (Recommended)

To enforce commit message standards and prevent invalid commits from reaching main:

### Step 1: Enable Branch Protection
1. Go to repository **Settings** → **Branches**
2. Click **Add rule** for `main` branch
3. Configure the following settings:

### Step 2: Required Status Checks
Enable these required checks before merging:
- ✅ **Validate Commit Messages** (from commitlint workflow)
- ✅ **Validate Databricks Bundle** (from CI/CD workflow)
- ✅ **Deploy to Development** (from CI/CD workflow)

### Step 3: Additional Protections
- ✅ **Require pull request reviews before merging**
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- ✅ **Restrict pushes that create matching branches** (only admins)

### Step 4: Result
With branch protection enabled:
- Invalid commit messages will **fail the commitlint check**
- PRs cannot be merged until **all commits follow conventional format**
- Automatic helpful comments guide developers to fix their commits
- Semantic versioning works reliably with proper commit messages

## Customization

### Adding New Jobs
1. Define job in `src/resources/jobs.yml`
2. Create corresponding notebooks in `src/notebooks/`
3. Update bundle targets in `src/databricks.yml` if needed

### Adding New Environments
1. Add target to `src/databricks.yml`
2. Create GitHub environment with appropriate protection rules
3. Add environment-specific secrets
4. Update workflow conditions in `.github/workflows/databricks-cicd.yml`

### Modifying Approval Gates
- Edit environment protection rules in GitHub repository settings
- Adjust workflow conditions for deployment triggers
- Update reviewer requirements and wait timers

## Troubleshooting

### Common Issues

1. **Bundle Validation Fails**
   - Check `src/databricks.yml` syntax
   - Verify workspace URLs and credentials
   - Ensure notebook paths exist

2. **Deployment Fails**
   - Verify Databricks CLI authentication
   - Check workspace permissions
   - Review job cluster configurations

3. **Tests Fail**
   - Check notebook execution logs in Databricks
   - Verify test data and table permissions
   - Review cluster resource allocation

### Getting Help
- Check Databricks Asset Bundles documentation
- Review GitHub Actions workflow logs
- Contact your platform team for workspace access issues

## Security Notes

- Never commit access tokens to the repository
- Use service principals for prod deployments
- Regularly rotate access tokens
- Follow principle of least privilege for workspace permissions
- Enable audit logging for prod workspaces