# Contributing to RehabYangu

We welcome contributions from the core development team. As this is a proprietary product, external pull requests are not accepted without prior agreement.

## Internal Development Process
1. Create a feature branch from `main`.
2. Keep commits small and focused.
3. Write clear commit messages following [Conventional Commits](https://www.conventionalcommits.org).
4. Ensure all tests pass and new features are covered by tests.
5. Update documentation in the `docs/` directory when applicable.
6. Open a merge request and request review from at least one other engineer.
7. Merge only after approval and all checks pass.

## Coding Standards
- **Backend**: Follow PEP 8, use Django best practices, avoid business logic in views.
- **Frontend**: Follow the component architecture outlined in `docs/frontend/`. Use TypeScript, Tailwind design tokens, and React Hook Form + Zod for all forms.
- **General**: No hard‑coded credentials, no commented‑out code, no dead imports.

## Documentation
Every new feature or architectural change must be reflected in the `docs/` folder. We treat documentation as part of the product.

## Communication
Use the project’s internal issue tracker and chat channels. Decisions that affect architecture must be documented in an ADR (Architecture Decision Record) – see `docs/architecture/`.

Thank you for helping build the future of healthcare in Africa.
