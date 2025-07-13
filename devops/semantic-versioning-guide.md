# Semantic Versioning and Conventional Commits Guide

## Overview
This guide explains how to use semantic versioning with conventional commits for the Databricks data platform CI/CD pipeline. Our automated versioning system creates releases based on your commit messages.

## Semantic Versioning (SemVer)

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes that require user intervention
- **MINOR** (0.1.0): New features that are backward compatible 
- **PATCH** (0.0.1): Bug fixes and improvements that are backward compatible

### Examples
- `v1.0.0` - Initial prod release
- `v1.1.0` - Added new data pipeline feature
- `v1.1.1` - Fixed data quality validation bug
- `v2.0.0` - Breaking change: updated schema format

## Conventional Commits

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types and Version Impact

| Commit Type | Description | Version Bump | Example |
|-------------|-------------|--------------|---------|
| `feat` | New feature | **MINOR** | `feat: add customer data pipeline` |
| `fix` | Bug fix | **PATCH** | `fix: resolve data quality validation error` |
| `perf` | Performance improvement | **PATCH** | `perf: optimize ETL processing speed` |
| `refactor` | Code refactoring | **PATCH** | `refactor: restructure data transformation logic` |
| `revert` | Revert previous change | **PATCH** | `revert: revert pipeline optimization` |
| `docs` | Documentation only | **No release** | `docs: update API documentation` |
| `style` | Code style changes | **No release** | `style: format code with black` |
| `test` | Add/update tests | **No release** | `test: add unit tests for data validation` |
| `chore` | Maintenance tasks | **No release** | `chore: update dependencies` |
| `ci` | CI/CD changes | **No release** | `ci: update GitHub Actions workflow` |
| `build` | Build system changes | **No release** | `build: update Databricks CLI version` |

### Breaking Changes (MAJOR)
To trigger a major version bump, add `!` after the type or add `BREAKING CHANGE:` in the footer:

```bash
# Option 1: Using ! notation
feat!: change data schema format

# Option 2: Using footer
feat: add new pipeline feature

BREAKING CHANGE: Updated data schema requires migration
```

## Examples

### Good Commit Messages

```bash
# New feature (minor version bump)
feat: add real-time data streaming pipeline
feat(etl): implement delta lake optimization
feat: add data quality monitoring dashboard

# Bug fixes (patch version bump)
fix: resolve memory leak in data processing
fix(validation): correct data type validation rules
fix: handle null values in customer data

# Performance improvements (patch version bump)
perf: optimize query performance for large datasets
perf(spark): increase parallelism for data processing

# Breaking changes (major version bump)
feat!: migrate from JSON to Parquet format
fix!: change API response structure

feat: update data pipeline architecture

BREAKING CHANGE: Pipeline configuration format has changed. 
Update your databricks.yml files according to the migration guide.

# No release commits
docs: update setup instructions
test: add integration tests for ETL pipeline
chore: upgrade Databricks CLI to latest version
ci: add semantic release workflow
```

### Bad Commit Messages (Avoid These)

```bash
# Too vague
fix: bug fix
feat: new feature
update: some changes

# Not following convention
Added new pipeline
Fixed the issue
Updates

# Missing description
feat:
fix:
```

## Scopes (Optional)

Use scopes to specify which part of the system is affected:

```bash
feat(etl): add data transformation step
fix(validation): resolve schema validation
perf(spark): optimize cluster configuration
docs(api): update endpoint documentation
```

### Common Scopes for Data Platform
- `etl` - Extract, Transform, Load processes
- `validation` - Data quality and validation
- `spark` - Spark configuration and optimization  
- `storage` - Data storage and Delta Lake
- `api` - API endpoints and interfaces
- `monitoring` - Observability and alerting
- `security` - Authentication and permissions
- `config` - Configuration management

## Workflow Integration

### How It Works
1. **Commit**: Push commits with conventional format to feature branches
2. **Validation**: Commitlint workflow automatically validates commit messages
3. **Merge**: Merge PR to main branch (only if commits are valid)
4. **Auto-Release**: Semantic release analyzes commits and creates version tag
5. **Auto-Deploy**: Production deployment triggers automatically from version tag

### Commit Message Enforcement
- **Automated Validation**: Every commit is checked against conventional commit standards
- **PR Blocking**: Invalid commits prevent PR merges when branch protection is enabled
- **Helpful Feedback**: Failed checks provide clear guidance on fixing commit messages
- **No Manual Intervention**: Once setup, enforcement is automatic

### Release Flow
```
feature/new-pipeline → PR → main → semantic-release → v1.2.0 tag → prod deployment
```

### Version Calculation Examples
Starting from `v1.0.0`:

```bash
# Scenario 1: Bug fixes only
fix: resolve data validation error
fix: handle edge case in processing
# Result: v1.0.1

# Scenario 2: New features  
feat: add customer segmentation pipeline
fix: resolve connection timeout
# Result: v1.1.0

# Scenario 3: Breaking change
feat!: migrate to new data format
# Result: v2.0.0
```

## Best Practices

### 1. Write Clear Descriptions
```bash
# Good
feat: add real-time customer data pipeline with Kafka integration

# Bad  
feat: add pipeline
```

### 2. Use Imperative Mood
```bash
# Good
fix: resolve timeout in data processing
feat: add data quality validation

# Bad
fixed timeout issue
added validation
```

### 3. Keep First Line Under 72 Characters
```bash
# Good
feat: implement incremental data loading for customer table

# Bad (too long)
feat: implement incremental data loading mechanism for customer table to improve performance and reduce processing time
```

### 4. Use Body for Detailed Explanation
```bash
feat: add automated data quality monitoring

Implement comprehensive data quality checks including:
- Schema validation for all incoming data
- Null value detection and reporting  
- Data freshness monitoring
- Anomaly detection for key metrics

Closes #123
```

### 5. Reference Issues
```bash
fix: resolve duplicate records in customer data

Fixes #456
Closes #789
```

## Manual Release Override

If you need to skip automatic release for a commit, use `[skip ci]` or `[no release]`:

```bash
docs: update README [skip ci]
chore: update dependencies [no release]
```

## Troubleshooting

### No Release Created
**Possible causes:**
- No conventional commits since last release
- Only docs/test/chore commits (these don't trigger releases)
- Commit messages don't follow conventional format

**Solution:** Ensure at least one `feat`, `fix`, `perf`, or `refactor` commit

### Wrong Version Bump
**Possible causes:**
- Incorrect commit type used
- Missing `!` for breaking changes

**Solution:** Follow conventional commit format exactly

### Release Failed
**Possible causes:**
- Missing GitHub permissions
- Network issues
- Invalid semantic-release configuration

**Solution:** Check GitHub Actions logs and repository permissions

## Configuration Files

The semantic versioning is configured through:

- **`.releaserc.json`** - Semantic release configuration
- **`.github/workflows/semantic-release.yml`** - GitHub Actions workflow
- **Conventional Commits** - Your commit messages drive the versioning

## Team Guidelines

### For Feature Development
1. Use `feat:` for new functionality
2. Use descriptive scopes when helpful
3. Write clear, concise descriptions
4. Reference relevant issues

### For Bug Fixes  
1. Use `fix:` for all bug corrections
2. Include issue numbers when available
3. Describe what was fixed, not just that it was fixed

### For Breaking Changes
1. Always use `!` notation or `BREAKING CHANGE:` footer
2. Explain the impact in the commit body
3. Provide migration guidance when needed
4. Coordinate with team before releasing

This automated versioning ensures every prod deployment is properly tagged and traceable, while maintaining consistency across the development lifecycle.