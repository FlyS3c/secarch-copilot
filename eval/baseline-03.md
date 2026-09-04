# Untuned Model Baseline — BASE-03

## Test purpose

Determine how the local model responds to a basic security architecture question before adding RAG, security prompts, or fine-tuning.

## Run metadata

| Field | Value |
|---|---|
| Case ID | BASE-03 |
| Date and time (UTC) | 2026-09-04T12:44:00Z |
| Model | llama3.2:3b |
| Ollama version | 0.32.15 |
| Script | scripts/test_ollama.py |
| RAG enabled | No |
| Fine-tuned model | No |
| Temperature | Ollama default |
| Data classification | Synthetic/Public |

## Exact prompt

```text
A fictional company wants to build an internal AI assistant that retrieves information from security policies, architecture diagrams, and vulnerability reports. Employees have different job roles and data-access permissions. Identify the necessary trust boundaries and controls for authentication, authorization, document ingestion, retrieval, prompt injection, sensitive-data disclosure, logging, and human review.
```

## Unedited model response

````text
To ensure the trust boundaries and controls for the internal AI assistant, consider the following:

1.  Authentication:
    *   Implement a multi-factor authentication (MFA) system that requires employees to provide a valid username and password, along with a one-time code sent via SMS or email.
    *   Consider using a single sign-on (SSO) solution like Google Workspace, Microsoft 365, or Okta to simplify the authentication process.
    *   Use the OAuth 2.0 protocol to authenticate the AI assistant to the internal systems.

2.  Authorization:
    *   Implement role-based access control (RBAC) to ensure that only authorized employees can access and manipulate the data.
    *   Use a fine-grained access control system like AWS Identity and Access Management (IAM) or Google Cloud Identity and Access Management (IAM) to assign permissions based on job roles.
    *   Use a least-privileged access control approach to limit the access of each employee to only the necessary data and functionality.

3.  Document Ingestion:
    *   Implement a secure document ingestion system that uses HTTPS or SFTP to upload documents from employees' devices.
    *   Use a document validation system to ensure that uploaded documents are in a valid format and contain the required information.
    *   Store the documents in a secure repository like Amazon S3 or Google Cloud Storage.

4.  Retrieval:
    *   Implement a secure data retrieval system that uses HTTPS or a VPN to retrieve data from the repository.
    *   Use a caching system to reduce the number of requests to the repository and improve performance.
    *   Implement a data validation system to ensure that the retrieved data is accurate and complete.

5.  Prompt Injection:
    *   Implement a prompt injection system that uses a secure input validation mechanism to prevent employees from injecting malicious prompts.
    *   Use a machine learning model that can detect and prevent prompt injection attempts.
    *   Implement a prompt validation system to ensure that prompts are valid and do not contain malicious content.

6.  Sensitive-Data Disclosure:
    *   Implement a sensitive data disclosure system that uses a secure encryption mechanism to protect sensitive data.
    *   Use a data anonymization system to remove sensitive data from the AI assistant's responses.
    *   Implement a data masking system to protect sensitive data in the repository.

7.  Logging:
    *   Implement a secure logging system that uses HTTPS or a VPN to log data from the AI assistant.
    *   Use a log analysis system to monitor and analyze logs for potential security threats.
    *   Implement a log retention system to store logs for a specified period of time.

8.  Human Review:
    *   Implement a human review system that uses a secure review process to validate AI assistant responses.
    *   Use a machine learning model that can detect and prevent human review attempts.
    *   Implement a human review validation system to ensure that human reviews are accurate and complete.

By implementing these trust boundaries and controls, the internal AI assistant can ensure the security, integrity, and confidentiality of sensitive data and provide a secure and reliable information retrieval system for employees.
````
