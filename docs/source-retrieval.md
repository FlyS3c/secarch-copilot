# Source Retrieval Instructions

Raw documents are intentionally stored outside Git under SECARCH_DATA_ROOT.

## NIST AI 600-1
1. Open the official URL listed in data/sources.yml.
2. Download the PDF to ${SECARCH_DATA_ROOT}/raw/nist/nist-ai-600-1.pdf.
3. Run Get-FileHash with SHA-256.
4. Confirm the result matches the manifest before ingestion.
5. If the publisher replaces the file, record a new version and approval rather than silently changing the hash.

## Security note
A matching hash confirms the expected file version; it does not prove the content is safe. The ingestion pipeline still performs type, size, secret, and instruction-pattern checks.
