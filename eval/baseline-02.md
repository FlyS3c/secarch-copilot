# Untuned Model Baseline — BASE-02

## Test purpose

Determine how the local model responds to a basic security architecture question before adding RAG, security prompts, or fine-tuning.

## Run metadata

| Field | Value |
|---|---|
| Case ID | BASE-02 |
| Date and time (UTC) | 2026-09-04T12:39:00Z |
| Model | llama3.2:3b |
| Ollama version | 0.32.15 |
| Script | scripts/test_ollama.py |
| RAG enabled | No |
| Fine-tuned model | No |
| Temperature | Ollama default |
| Data classification | Synthetic/Public |

## Exact prompt

```text
A fictional financial services company wants customers to upload confidential documents through a web portal. Files are stored in Azure Blob Storage and transferred to a third-party processing company through an API. Perform a security architecture review covering identity, encryption, network security, file validation, logging, data retention, and third-party risk. Do not assume unspecified controls exist.
```

## Unedited model response

````text
**Security Architecture Review: Confidential Document Uploads**

**I. Identity and Access Control**

1. **Authentication**: The web portal should use a robust authentication mechanism, such as OAuth 2.0 or OpenID Connect, to verify the identity of users uploading documents. Ensure that authentication tokens are not stored in plain text or transmitted insecurely.
2. **Authorization**: Implement fine-grained access controls to restrict access to files stored in Azure Blob Storage based on user roles or permissions. Utilize Azure's built-in RBAC (Role-Based Access Control) or a custom solution.
3. **Multi-Factor Authentication**: Consider adding an MFA layer to ensure an additional layer of security, especially for high-risk users or critical document uploads.

**II. Encryption**

1. **Data at Rest**: Ensure that all uploaded files are stored in Azure Blob Storage with proper encryption. Use Azure's Server-Side Encryption (SSE) or customer-managed keys (CMK) to protect sensitive data.
2. **Data in Transit**: Implement Transport Layer Security (TLS) to encrypt data during transmission between the web portal and Azure Blob Storage. Use the latest TLS version (TLS 1.3) and key exchange algorithms (e.g., ECDHE).
3. **Client-Side Encryption**: Consider using client-side encryption to protect files on the user's device before uploading them to Azure Blob Storage. This adds an additional layer of security, but requires careful planning and execution.

**III. Network Security**

1. **HTTP/HTTPS**: Ensure the web portal uses HTTPS (TLS) to encrypt communication with Azure Blob Storage and the third-party processing company.
2. **Firewalls and Access Control Lists**: Configure firewalls and access control lists to restrict access to Azure Blob Storage and the third-party processing company based on IP addresses, ports, or user roles.
3. **Regular Security Updates**: Regularly update the web portal, Azure Blob Storage, and third-party processing company with the latest security patches and updates.

**IV. File Validation**

1. **Content Validation**: Implement a content validation mechanism to verify the integrity and authenticity of uploaded files. Use digital signatures, checksums, or message authentication codes (MACs).
2. **File Format Validation**: Validate the file format and structure to ensure only authorized files are uploaded and processed.
3. **File Reputation Checks**: Perform reputation checks on uploaded files to detect potential malware or suspicious activity.

**V. Logging and Monitoring**

1. **Audit Logs**: Implement a comprehensive logging mechanism to track user activity, file uploads, and API calls. Use Azure's built-in logging capabilities or a custom solution.
2. **Real-Time Monitoring**: Set up real-time monitoring to detect potential security incidents, such as unauthorized file access or API abuse.
3. **Incident Response**: Establish an incident response plan to quickly respond to security incidents and minimize potential damage.

**VI. Data Retention**

1. **Data Retention Policy**: Develop a data retention policy that outlines the duration for which files are stored in Azure Blob Storage and the third-party processing company.
2. **Data Deletion**: Implement a mechanism to securely delete files after the retention period has expired.
3. **Regular Data Review**: Regularly review stored files to detect potential data breaches or unauthorized access.

**VII. Third-Party Risk**

1. **Vendor Risk Assessment**: Conduct a thorough risk assessment of the third-party processing company, including their security posture, compliance with relevant regulations, and reputation.
2. **Contractual Requirements**: Ensure the third-party processing company agrees to meet specific security and compliance requirements, including data encryption, access controls, and incident response.
3. **Regular Security Audits**: Conduct regular security audits of the third-party processing company to ensure they maintain their security posture and comply with contractual requirements.

By addressing these security architecture concerns, the financial services company can ensure a secure and compliant environment for confidential document uploads, while minimizing the risk of data breaches or unauthorized access.
````
