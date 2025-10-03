# Contributing to BiScheduler

## 🤝 Collaboration Guidelines

### Branch Naming Convention
- `feature/` - New features (e.g., `feature/add-export`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-dark-mode`)
- `docs/` - Documentation (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/css-architecture`)

### Workflow
1. **Always** fetch before starting work: `git fetch origin`
2. **Create** a new branch from master for your work
3. **Make** small, focused commits with clear messages
4. **Push** your branch to origin
5. **Create** a Pull Request for review
6. **Never** push directly to master without review

### Commit Message Format
```
<type>: <short description>

<longer explanation if needed>

Co-Authored-By: Name <email>
```

Types: feat, fix, docs, refactor, test, chore

### Before Pushing
- Run tests: `python -m pytest`
- Check for conflicts: `git pull origin master`
- Review your changes: `git diff master`

### Communication
- Use Pull Request descriptions to explain changes
- Tag team members for review with @username
- Document breaking changes clearly
- Update PROJECT_MASTER_DOCUMENTATION.md for major features

### Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass successfully
- [ ] Documentation updated if needed
- [ ] No sensitive data exposed
- [ ] Database migrations included if needed