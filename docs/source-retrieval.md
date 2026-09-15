# Source Retrieval Instructions

Raw source documents are intentionally stored outside Git under `SECARCH_DATA_ROOT`. The repository contains the approved source manifest, expected SHA-256 hashes, source metadata, and ingestion controls, but it does not redistribute third-party source documents.

Only records marked `approved: true` in `data/sources.yml` may be parsed, chunked, embedded, or indexed.

## Approved sources

| Source                                      | Retrieval location                                                                                                                          | Local path under `SECARCH_DATA_ROOT`                 | License or terms       |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ---------------------- |
| OWASP Authentication Cheat Sheet            | [OWASP GitHub source](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Authentication_Cheat_Sheet.md)            | `raw/owasp/Authentication_Cheat_Sheet.md`            | CC BY-SA 4.0           |
| NIST SP 800-53 Revision 5                   | [NIST publication](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf)                                              | `raw/nist/NIST.SP.800-53r5.pdf`                      | NIST publication terms |
| NIST AI RMF 1.0                             | [NIST publication](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)                                                                  | `raw/nist/NIST.AI.100-1.pdf`                         | NIST publication terms |
| NIST AI RMF Generative AI Profile           | [NIST publication](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)                                                                  | `raw/nist/NIST.AI.600-1.pdf`                         | NIST publication terms |
| NIST Cybersecurity Framework 2.0            | [NIST publication](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf)                                                                 | `raw/nist/NIST.CSWP.29.pdf`                          | NIST publication terms |
| NIST SP 800-160 Volume 1 Revision 1         | [NIST publication](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-160v1r1.pdf)                                           | `raw/nist/NIST.SP.800-160v1r1.pdf`                   | NIST publication terms |
| NIST SP 800-207                             | [NIST publication](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)                                               | `raw/nist/NIST.SP.800-207.pdf`                       | NIST publication terms |
| OWASP GenAI LLM Top 10 2026                 | [OWASP project page](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)                                                         | `raw/owasp/OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf`     | CC BY-SA 4.0           |
| OWASP Secure Cloud Architecture Cheat Sheet | [OWASP GitHub source](https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Secure_Cloud_Architecture_Cheat_Sheet.md) | `raw/owasp/Secure_Cloud_Architecture_Cheat_Sheet.md` | CC BY-SA 4.0           |

The authoritative versions, retrieval dates, expected hashes, approval metadata, roles, and classifications are recorded in `data/sources.yml`.

## Retrieve the directly downloadable sources

Set the data root to the same value used in `.env`:

```powershell
$DataRoot = "C:\SecArchCopilotData"
$env:SECARCH_DATA_ROOT = $DataRoot

$Sources = [ordered]@{
  "raw\owasp\Authentication_Cheat_Sheet.md" = "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Authentication_Cheat_Sheet.md"
  "raw\nist\NIST.SP.800-53r5.pdf" = "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf"
  "raw\nist\NIST.AI.100-1.pdf" = "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
  "raw\nist\NIST.AI.600-1.pdf" = "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf"
  "raw\nist\NIST.CSWP.29.pdf" = "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf"
  "raw\nist\NIST.SP.800-160v1r1.pdf" = "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-160v1r1.pdf"
  "raw\nist\NIST.SP.800-207.pdf" = "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf"
  "raw\owasp\Secure_Cloud_Architecture_Cheat_Sheet.md" = "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets/Secure_Cloud_Architecture_Cheat_Sheet.md"
}

foreach ($RelativePath in $Sources.Keys) {
  $Destination = Join-Path $DataRoot $RelativePath

  New-Item `
    -ItemType Directory `
    -Force `
    -Path (Split-Path $Destination) |
    Out-Null

  Invoke-WebRequest `
    -Uri $Sources[$RelativePath] `
    -OutFile $Destination
}
```

## Retrieve the OWASP GenAI document

The manifest records an OWASP project page rather than a stable direct PDF URL. Open the project page, download the version identified in `data/sources.yml`, and save it as:

```text
C:\SecArchCopilotData\raw\owasp\OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf
```

Do not replace the manifest hash merely to accommodate a changed download. Treat a hash change as a new source version requiring review and approval.

## Validate the corpus

From the repository root, run the secure ingestion pipeline without writing embeddings or Chroma records:

```powershell
python .\scripts\ingest.py `
  --manifest .\data\sources.yml `
  --dry-run
```

The dry run validates manifest uniqueness, approval status, file paths, file types, sizes, SHA-256 values, extracted content, and instruction or secret indicators. It must complete successfully before indexing.

To create a versioned index after validation:

```powershell
python .\scripts\ingest.py `
  --manifest .\data\sources.yml `
  --collection secarch_knowledge_YYYY_MM_DD_v1
```

Test the new collection before setting it as `SECARCH_ACTIVE_COLLECTION` in `.env`.

## Restricted reference records

The following SABSA records are intentionally classified as `restricted` and marked `approved: false`:

* `sabsa-r100-security-services-catalogue`
* `sabsa-r101-matrices-2018-release-notes`
* `sabsa-w100-white-paper`
* `sabsa-w101-architecting-secure-digital-world`
* `sabsa-w102-meaning-of-risk`
* `sabsa-w103-responsibility-assignment-modelling`
* `sabsa-w117-togaf-integration`
* `sabsa-w105-enterprise-security-architecture-principles`

These records are reference-only. Do not parse, chunk, embed, index, publish, or use them for AI retrieval without written permission from the applicable rights holders. The ingestion pipeline skips unapproved records.

## Source update procedure

When a publisher changes a source:

1. Do not overwrite the approved file silently.
2. Record the new retrieval date and version.
3. Calculate and review the new SHA-256 value.
4. Review the source’s license, classification, and content.
5. Update the manifest approval metadata.
6. Run the ingestion dry run.
7. Build and test a new versioned collection.
8. Retain the previous collection until rollback testing is complete.

## Security notes

A matching SHA-256 value confirms that a file matches the reviewed version; it does not prove that its contents are safe. The ingestion pipeline still applies type, size, content, approval, and quarantine controls.

Never place employer information, customer data, secrets, licensed training material, restricted documents, Chroma data, or raw source files in Git.
