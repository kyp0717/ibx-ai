# TWS Trading App - Development Context
Interactive Brokers trading application using Python and IBAPI.

## Project Awareness
**At conversation start, read**:
- `context/implement-plan/*.md` - Architecture, style, constraints
- `context/tasks.md` - Current progress and feature status
- `context/requirements.md` - Technical specifications
- `context/logs/*.md` - Completed features and issues

## File Organization
All generated content goes in `context/` submodule:

- **docs/** - Documentation and guides
- **logs/** - Feature summaries (format: feature_xx_yyyymmdd.md)

### Log Requirements
- Create summary when feature completes successfully (max 16 lines)
- Format: feature_xx_yyyymmdd.md with datestamp/timestamp
- Include: 1 heading + bullet points (no icons)
- Append updates to existing feature logs with timestamp
- Be concisel.

## Development Guidelines

### General Principles
- Never assume missing context - ask questions if uncertain
- Never hallucinate libraries or functions
- Confirm file paths and module names exist before referencing
- Never delete/overwrite existing code unless instructed or from tasks.md

### Development Permissions
**ALWAYS request permission before**:
- Adding new features, methods, or functions
- Modifying existing modules beyond bug fixes
- Creating new files or directories
- Implementing "nice-to-have" features

### Focus & Completion
- Complete one well-defined feature before moving to next
- **Definition of Done**: Tests written/passing, verified in target environment, integration confirmed, documentation updated
- **NO FEATURE CREEP**: Resist nice-to-have additions until core feature is 100% complete

### Code Style
- Never add comments unless requested
- Match existing code conventions and patterns
- Use existing libraries - check package.json/cargo.toml/etc first
- Follow security best practices - no hardcoded secrets/keys
- Use .env files for configuration
- Max 500 lines per file - refactor if approaching limit

## Testing Requirements
- **CRITICAL**: Use tws-test-agent agent 
- If the subagent does not exist create using definition from `context/agents/tws-test-agent.md`.
- Use uv virtual environment for all testing
- Store tests in `tests/` folder
- Update existing unit tests when logic changes
- Do not update README.md after testing

## Feature Development Pattern
When adding new features:

1. **Module Structure**
   - Create new file in `src/` named after feature
   - Define main struct and result types

2. **Testing**
   - Create unit tests in `tests/test_your_feature_unit.py`
   - Follow strict TDD: RED → GREEN → REFACTOR
   - Each feature must be independent and self-contained

3. **Scripts**
   - Create new scripts and save to `scripts/` folder
   - Shell scripts and automation

## Documentation Requirements
- Update README.md only when: features added, dependencies change, setup modified
- Comment only non-obvious code
- Add `# Reason:` comments for complex logic explaining why, not what

## Important Reminders
- Do what's asked - nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files over creating new ones
- NEVER proactively create documentation (*.md) unless explicitly requested