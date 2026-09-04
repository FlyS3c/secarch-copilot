from ollama import chat

response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": (
                "A fictional company wants to build an internal AI assistant that retrieves information from security policies, architecture diagrams, and vulnerability reports. "
                "Employees have different job roles and data-access permissions. "
                "Identify the necessary trust boundaries and controls for authentication, authorization, document ingestion, retrieval, prompt injection, sensitive-data disclosure, logging, and human review."
            ),
        }
    ],
)

print(response.message.content)