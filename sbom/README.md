# Software Bill of Materials

This directory contains a point-in-time SBOM for the hardened SecArch Copilot container image.

## Provenance

- Format: CycloneDX JSON 1.6
- Generated UTC: 2026-09-15T15:28:39Z
- Source commit: 339f7936adf356f607f9fd147837a3e57b75b8f1
- Application image ID: sha256:eb619175002c8eddbb3f5e8ec037ed645f2996805027f2daa24ca46572303972
- Generator: Syft 1.51.1
- Generator image: anchore/syft@sha256:95fe0835e5bebc6f8b1f8acef68d47d63d594ef4c0f25c097ff853b23cbac74c
- Components recorded: 3045
- SBOM SHA-256: bdf9fc8032f5dc01517835ac3e72de721715801e3bb7e623c212ebcd613d6d36

## Scope

The SBOM was generated from the local secarch-copilot:local Linux container image. It includes Python dependencies, operating-system packages, applications, and identified files.

The SBOM is a point-in-time inventory, not proof that the image is vulnerability-free. Known ChromaDB findings and compensating controls are documented in docs/dependency-risk-register.md.

Before publication, the SBOM was checked for local user paths, API-key assignments, Semgrep token assignments, placeholder credentials, and bundled environment files.
