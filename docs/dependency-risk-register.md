# Dependency Risk Register

## ChromaDB 1.5.9

| Field | Value |
|---|---|
| Dependency | `chromadb==1.5.9` |
| Status | Temporarily accepted |
| Scope | Controlled local portfolio demonstrations only |
| Decision date | 2026-09-15 |
| Review deadline | 2026-10-15 |
| Owner | Project maintainer |

### Vulnerabilities

| Identifier | Severity | Description |
|---|---|---|
| CVE-2026-45829 / PYSEC-2026-311 | Critical | Pre-authentication code injection through the ChromaDB Python FastAPI collection-creation endpoint |
| CVE-2026-45833 / PYSEC-2026-3814 | Critical | Authenticated code injection through the ChromaDB Python FastAPI collection-update endpoint |
| CVE-2026-45830 / PYSEC-2026-3813 | High | Insufficient tenant authorization validation |
| CVE-2026-45831 / PYSEC-2026-3815 | High | SimpleRBACAuthorizationProvider does not enforce resource scope |

### Applicability

SecArch Copilot uses `chromadb.PersistentClient` as an embedded local database. It does not run or expose ChromaDB's Python FastAPI server or its collection-management HTTP endpoints.

The application does not accept user-controlled embedding-function configurations or enable `trust_remote_code`. The supported container deployment exposes the application only through a localhost-bound port and runs as a non-root user.

The authorization vulnerabilities apply to ChromaDB server and multi-tenant authorization paths that are not used by the current architecture.

### Decision

The dependency remains genuinely vulnerable, so these findings are not classified as false positives. Risk is temporarily accepted because no patched ChromaDB release is currently available and the vulnerable server paths are not exposed by the supported deployment.

Production deployment is not approved while these exceptions remain active.

### Compensating Controls

- Use embedded `PersistentClient` mode only.
- Do not start or expose the ChromaDB Python FastAPI server.
- Bind the SecArch Copilot API to localhost for demonstrations.
- Do not accept user-controlled ChromaDB collection or embedding configuration.
- Do not enable `trust_remote_code`.
- Run the container as the non-root `secarch` user.
- Retain application-layer tenant, role, classification, and source-approval filters.
- Use controlled synthetic or public demonstration data only.

### Review Triggers

Review this decision immediately if:

- ChromaDB publishes a patched version.
- The project moves to Chroma client/server mode.
- Any ChromaDB endpoint becomes network-accessible.
- User input can influence collection or embedding configuration.
- The application is considered for production use.
- The review deadline is reached.

### Scanner Treatment

`pip-audit` exceptions are explicitly listed in the CI workflow. Semgrep Supply Chain reported eight records representing two vulnerabilities repeated across four lockfiles. Those records were triaged as temporarily accepted risk with the same architectural restrictions documented here.

### References

- [CVE-2026-45829](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c)
- [CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf)
- [PYSEC-2026-3813](https://osv.dev/vulnerability/PYSEC-2026-3813)
- [PYSEC-2026-3815](https://osv.dev/vulnerability/PYSEC-2026-3815)
- [ChromaDB on PyPI](https://pypi.org/project/chromadb/)