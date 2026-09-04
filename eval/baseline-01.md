# Untuned Model Baseline — BASE-01

## Test purpose

Determine how the local model responds to a basic security architecture question before adding RAG, security prompts, or fine-tuning.

## Run metadata

| Field | Value |
|---|---|
| Case ID | BASE-01 |
| Date and time (UTC) | 2026-09-04T12:30:00Z |
| Model | llama3.2:3b |
| Ollama version | 0.32.15 |
| Script | scripts/test_ollama.py |
| RAG enabled | No |
| Fine-tuned model | No |
| Temperature | Ollama default |
| Data classification | Synthetic/Public |

## Exact prompt

```text
A fictional company stores public files in Azure Blob Storage. List three security questions an architect should ask.
```

## Unedited model response

````text
As an architect, here are three security questions you should ask when considering storing public files in Azure Blob Storage:

1. **What access controls will be in place to restrict who can read and download files from the container?**

The architect should ask to ensure that the container is not publicly accessible, and that only authorized users or applications can access the files. This may involve implementing:
        * Azure Blob Storage permissions, such as Container and Object-level permissions.
        * Azure Active Directory (AAD) or other authentication mechanisms to authenticate users and applications before granting access to the files.
        * Role-based access control (RBAC) to define permissions for users and applications.

2. **How will malicious or unauthorized users attempt to access or download the files, and what measures will be taken to prevent or mitigate these attempts?**

The architect should ask to identify potential vulnerabilities in the storage configuration and the measures in place to prevent unauthorized access or malicious activity. This may include:
        * Monitoring the storage account for suspicious activity, such as unusual access patterns or IP addresses.
        * Implementing Azure Security Center to monitor and alert on potential security threats.
        * Regularly reviewing and updating storage access permissions to ensure they are still necessary and not vulnerable to exploitation.

3. **What measures will be taken to protect the files from unauthorized modification or tampering, and how will changes to the file metadata or content be tracked?**

The architect should ask to ensure that the files are protected from unauthorized modification or tampering, and that any changes to the file metadata or content are tracked and audited. This may involve:
        * Implementing versioning and checksums to track changes to file metadata and content.
        * Using Azure Storage Events to trigger notifications when files are accessed, modified, or deleted.
        * Regularly backing up and archiving files to prevent loss of data in case of storage account compromise.

By asking these security questions, the architect can ensure that the public file storage is properly secured and protected from unauthorized access, modification, or tampering.
````
