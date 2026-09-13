"use strict";

const API_BASE_URL = "http://127.0.0.1:8000";
const FRONTEND_TIMEOUT_MS = 190000;

const form = document.querySelector("#review-form");
const workflowInput = document.querySelector("#workflow");
const apiKeyInput = document.querySelector("#api-key");
const submitButton = document.querySelector("#submit-button");
const requestStatus = document.querySelector("#request-status");
const resultsPanel = document.querySelector("#results");
const resultsTitle = document.querySelector("#results-title");
const threatModelFields = document.querySelector(
    "#threat-model-fields"
);
const dataFlowsInput = document.querySelector("#data-flows");
const architectureResults = document.querySelector(
    "#architecture-results"
);
const threatModelResults = document.querySelector(
    "#threat-model-results"
);

function linesFrom(fieldId) {
    return document
        .querySelector(fieldId)
        .value
        .split(/\r?\n/)
        .map((value) => value.trim())
        .filter((value) => value.length > 0);
}

function setStatus(message, type = "") {
    requestStatus.textContent = message;
    requestStatus.className = `status ${type}`.trim();
}

function renderList(elementId, values, emptyMessage) {
    const container = document.querySelector(elementId);
    container.replaceChildren();

    const displayedValues =
        Array.isArray(values) && values.length > 0
            ? values
            : [emptyMessage];

    for (const value of displayedValues) {
        const item = document.createElement("li");
        item.textContent = String(value);
        container.appendChild(item);
    }
}

function addLabeledParagraph(container, label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");

    strong.textContent = `${label}: `;
    paragraph.appendChild(strong);
    paragraph.appendChild(document.createTextNode(String(value)));
    container.appendChild(paragraph);
}

function addSeverity(container, itemId, severityValue) {
    const heading = document.createElement("div");
    heading.className = "finding-heading";

    const title = document.createElement("h4");
    title.textContent = itemId;

    const severity = document.createElement("span");
    const allowedSeverities = new Set(["low", "medium", "high"]);
    const safeSeverity = allowedSeverities.has(severityValue)
        ? severityValue
        : "medium";

    severity.className = `severity severity-${safeSeverity}`;
    severity.textContent = safeSeverity;

    heading.appendChild(title);
    heading.appendChild(severity);
    container.appendChild(heading);
}

function addCitations(container, citationsValue) {
    const citationHeading = document.createElement("strong");
    citationHeading.textContent = "Citations:";
    container.appendChild(citationHeading);

    const citationList = document.createElement("ul");
    citationList.className = "citation-list";

    const citations = Array.isArray(citationsValue)
        ? citationsValue
        : [];

    for (const citation of citations) {
        const item = document.createElement("li");
        item.textContent =
            `${citation.source_id} | ${citation.chunk_id} | ` +
            `${citation.page_or_section}`;
        citationList.appendChild(item);
    }

    if (citations.length === 0) {
        const item = document.createElement("li");
        item.textContent = "No validated citation returned.";
        citationList.appendChild(item);
    }

    container.appendChild(citationList);
}

function renderFindings(findings) {
    const container = document.querySelector("#findings-list");
    container.replaceChildren();

    if (!Array.isArray(findings) || findings.length === 0) {
        const message = document.createElement("p");
        message.textContent =
            "No supported findings were returned. Review the missing " +
            "information and limitations sections.";
        container.appendChild(message);
        return;
    }

    for (const finding of findings) {
        const card = document.createElement("article");
        card.className = "finding-card";

        addSeverity(
            card,
            `Finding ${finding.finding_id}`,
            finding.severity
        );

        addLabeledParagraph(card, "Risk", finding.risk);
        addLabeledParagraph(
            card,
            "Recommendation",
            finding.recommendation
        );

        addCitations(card, finding.citations);

        addLabeledParagraph(
            card,
            "Human review required",
            finding.human_review_required ? "Yes" : "No"
        );

        container.appendChild(card);
    }
}

function renderThreats(threats) {
    const container = document.querySelector("#threats-list");
    container.replaceChildren();

    if (!Array.isArray(threats) || threats.length === 0) {
        const message = document.createElement("p");
        message.textContent =
            "No supported threats were returned. Review the missing " +
            "information and limitations sections.";
        container.appendChild(message);
        return;
    }

    for (const threat of threats) {
        const card = document.createElement("article");
        card.className = "finding-card";

        addSeverity(
            card,
            `Threat ${threat.threat_id}`,
            threat.severity
        );

        addLabeledParagraph(
            card,
            "Category",
            threat.category
        );

        addLabeledParagraph(
            card,
            "Threat",
            threat.threat
        );

        const affectedAssets =
            Array.isArray(threat.affected_assets) &&
            threat.affected_assets.length > 0
                ? threat.affected_assets.join(", ")
                : "No affected assets listed.";

        addLabeledParagraph(
            card,
            "Affected assets",
            affectedAssets
        );

        addLabeledParagraph(
            card,
            "Mitigation",
            threat.mitigation
        );

        addLabeledParagraph(
            card,
            "Residual risk",
            threat.residual_risk
        );

        addCitations(card, threat.citations);

        addLabeledParagraph(
            card,
            "Human review required",
            threat.human_review_required ? "Yes" : "No"
        );

        container.appendChild(card);
    }
}

function renderCommonResults(result) {
    document.querySelector("#summary").textContent =
        result.summary || "No summary returned.";

    renderList(
        "#assumptions",
        result.assumptions,
        "No assumptions listed."
    );

    renderList(
        "#missing-information",
        result.missing_information,
        "No missing information listed."
    );

    renderList(
        "#limitations",
        result.limitations,
        "No limitations listed."
    );
}

function renderArchitectureReview(review) {
    renderCommonResults(review);

    architectureResults.hidden = false;
    threatModelResults.hidden = true;
    resultsTitle.textContent = "Architecture review draft";

    renderFindings(review.findings);
}

function renderThreatModel(threatModel) {
    renderCommonResults(threatModel);

    architectureResults.hidden = true;
    threatModelResults.hidden = false;
    resultsTitle.textContent = "Threat model draft";

    renderList(
        "#assets",
        threatModel.assets,
        "No assets listed."
    );

    renderList(
        "#trust-boundaries",
        threatModel.trust_boundaries,
        "No trust boundaries listed."
    );

    renderThreats(threatModel.threats);

    renderList(
        "#residual-risk-questions",
        threatModel.residual_risk_questions,
        "No residual-risk questions listed."
    );
}

function displayResults(workflow, responseBody) {
    if (workflow === "threat-model") {
        renderThreatModel(responseBody);
    } else {
        renderArchitectureReview(responseBody);
    }

    resultsPanel.hidden = false;
    resultsPanel.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}

function buildArchitectureRequest() {
    return {
        system_name: document.querySelector("#system-name").value.trim(),
        purpose: document.querySelector("#purpose").value.trim(),
        components: linesFrom("#components"),
        data_classes: linesFrom("#data-classes"),
        identities: linesFrom("#identities"),
        integrations: linesFrom("#integrations"),
        network_boundaries: linesFrom("#network-boundaries"),
    };
}

function buildRequest(workflow) {
    const requestBody = buildArchitectureRequest();

    if (workflow === "threat-model") {
        requestBody.data_flows = linesFrom("#data-flows");
    }

    return requestBody;
}

function configureWorkflow() {
    const isThreatModel = workflowInput.value === "threat-model";

    threatModelFields.hidden = !isThreatModel;
    dataFlowsInput.required = isThreatModel;
    submitButton.textContent = isThreatModel
        ? "Generate threat model"
        : "Generate review";

    resultsPanel.hidden = true;
    setStatus("");
}

workflowInput.addEventListener("change", configureWorkflow);

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
        return;
    }

    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
        setStatus("Enter the local API key.", "error");
        return;
    }

    const workflow = workflowInput.value;
    const workflowLabel =
        workflow === "threat-model"
            ? "threat model"
            : "architecture review";

    submitButton.disabled = true;
    resultsPanel.hidden = true;

    setStatus(
        `Generating the ${workflowLabel}. ` +
        "This may take up to 180 seconds."
    );

    const controller = new AbortController();
    const timeoutId = window.setTimeout(
        () => controller.abort(),
        FRONTEND_TIMEOUT_MS
    );

    try {
        const response = await fetch(
            `${API_BASE_URL}/v1/${workflow}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey,
                },
                body: JSON.stringify(buildRequest(workflow)),
                signal: controller.signal,
            }
        );

        const responseText = await response.text();
        let responseBody = {};

        if (responseText) {
            try {
                responseBody = JSON.parse(responseText);
            } catch {
                throw new Error(
                    "The API returned an unreadable response."
                );
            }
        }

        if (!response.ok) {
            const detail =
                typeof responseBody.detail === "string"
                    ? responseBody.detail
                    : `Request failed with status ${response.status}.`;

            throw new Error(detail);
        }

        displayResults(workflow, responseBody);

        setStatus(
            `${workflowLabel} generated successfully.`,
            "success"
        );
    } catch (error) {
        resultsPanel.hidden = true;

        if (error.name === "AbortError") {
            setStatus(
                "The browser stopped waiting for the local API.",
                "error"
            );
        } else {
            setStatus(
                error.message || "The request failed.",
                "error"
            );
        }
    } finally {
        window.clearTimeout(timeoutId);
        submitButton.disabled = false;
    }
});

form.addEventListener("reset", () => {
    window.setTimeout(() => {
        configureWorkflow();
    }, 0);
});

configureWorkflow();