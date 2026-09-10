# Pythia implementation decisions

## 2026-09-09

- Kept the existing MLP/harness and manuscript immutable.
- Added a separate policy-grounded synthetic benchmark because opaque token
  templates cannot support a meaningful language-model validity claim.
- Kept public model input and private annotation files separately joinable by
  `public_id`; the model receives no gold labels or template identifiers.
- Fixed one public action catalogue across rows and variants.
- Added an independent fact/rule interpreter. It is a project-authored oracle
  for fictional policies, not human adjudication or moral ground truth.
- Added typed graph canonicalization with separate structure and relation
  fingerprints. Node IDs are excluded from metamorphic identity.
- Made Pythia dependencies optional and isolated. The loader pins the reviewed
  checkpoint SHA, disallows remote code, and rejects generic architectures.
- Locked comparison remains blocked until a clean, owner-approved commit and a
  measured resource plan exist.

