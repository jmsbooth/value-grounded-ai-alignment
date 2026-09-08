# Security policy

This repository contains research code and illustrative ontology fixtures. It is not a production alignment, authorization, or safety-verification system. The toy verifier is deliberately limited and must not be used to approve real-world actions.

## Reporting

Please do not include secrets, personal data, or exploit instructions in issues. For a suspected security defect in the repository itself, open a private GitHub security advisory when available. If that is not available, contact the repository owner through the public profile associated with `jmsbooth` and provide a minimal reproduction without sensitive payloads.

## Research threat model

The paper treats prompt injection, ontology poisoning, world-state poisoning, normative drift, axiology corruption, expert-routing manipulation, verifier bypass, specification gaming, conflicting authorities, and governance compromise as distinct risks. Proposed mitigations are hypotheses and require adversarial evaluation.

## Maintainer expectations

- Never commit credentials, tokens, private datasets, or proprietary implementation details.
- Keep generated artifacts reproducible from tracked sources.
- Record ontology changes with provenance, validation, regression evaluation, and explicit governance approval.
- Do not represent a passing toy test as evidence of alignment or formal safety.
