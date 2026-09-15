# Software Bill of Materials

This directory contains a point-in-time SBOM for the hardened SecArch Copilot container image.

## Provenance

* Format: CycloneDX JSON 1.7
* Generated UTC: 2026-09-15T18:24:10Z
* Source commit: 602352f93bd89fdaca45e80bfff0841244f4e4fa
* Application image ID: sha256:33d9113a0f83dd16ed31c1a434acfcb6f85b42fb01f05575aafee9b19c373848
* Generator: Syft 1.51.1
* Generator image: anchore/syft@sha256:95fe0835e5bebc6f8b1f8acef68d47d63d594ef4c0f25c097ff853b23cbac74c
* Components recorded: 3045
* SBOM SHA-256: fe065931991fdc2298d5cfb43627b0b3c06d2284f97a0b0f67a4e6a848be8712

## Scope

The SBOM was generated from the local `secarch-copilot:local` Linux container image. It includes Python dependencies, operating-system packages, applications, and identified files.

The SBOM is a point-in-time inventory, not proof that the image is vulnerability-free. Known ChromaDB findings and compensating controls are documented in `docs/dependency-risk-register.md`.

Before publication, the SBOM was checked for local user paths, API-key assignments, Semgrep token assignments, placeholder credentials, and bundled environment files.
