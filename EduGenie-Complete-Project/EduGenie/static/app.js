const taskEl = document.getElementById("task");
const inputEl = document.getElementById("inputText");
const inputLabelEl = document.getElementById("inputLabel");
const submitBtn = document.getElementById("submitBtn");
const clearBtn = document.getElementById("clearBtn");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const resultTitle = document.getElementById("resultTitle");
const resultEl = document.getElementById("result");
const copyBtn = document.getElementById("copyBtn");

const taskConfig = {
    qa: {
        label: "Question",
        placeholder: "Example: Which is the largest ocean?",
        button: "Get Answer",
        title: "Answer"
    },
    explain: {
        label: "Topic",
        placeholder: "Example: Explain the Pythagoras theorem",
        button: "Explain",
        title: "Explanation"
    },
    quiz: {
        label: "Passage or topic",
        placeholder: "Paste a passage or enter a topic such as 'Pythagoras theorem'.",
        button: "Generate Quiz",
        title: "Quiz"
    },
    summarize: {
        label: "Educational text",
        placeholder: "Paste the paragraph or notes you want to summarize.",
        button: "Summarize",
        title: "Summary"
    },
    learn: {
        label: "Topic",
        placeholder: "Example: SQL",
        button: "Get Learning Path",
        title: "Learning Path"
    }
};

function setTaskUI() {
    const config = taskConfig[taskEl.value];
    inputLabelEl.textContent = config.label;
    inputEl.placeholder = config.placeholder;
    submitBtn.textContent = config.button;
    resultTitle.textContent = config.title;
    statusEl.textContent = "";
    statusEl.className = "status";
}

function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.className = isError ? "status error" : "status";
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function renderText(text, className = "answer") {
    resultEl.innerHTML = `<div class="${className}">${escapeHtml(text)}</div>`;
}

function renderQuiz(data) {
    const questions = data.questions || [];
    resultEl.innerHTML = `
        <p><strong>${escapeHtml(data.title || "Practice Quiz")}</strong></p>
        ${questions.map((q, i) => `
            <article class="quiz-question" data-answer="${q.answer_index}">
                <h3>${i + 1}. ${escapeHtml(q.question)}</h3>
                ${q.options.map((option, index) => `
                    <label class="option">
                        <input type="radio" name="q-${i}" value="${index}">
                        <span>${escapeHtml(option)}</span>
                    </label>
                `).join("")}
                <button class="check-answer" type="button">Check Answer</button>
                <div class="feedback"></div>
            </article>
        `).join("")}
    `;

    document.querySelectorAll(".check-answer").forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".quiz-question");
            const correctIndex = Number(card.dataset.answer);
            const selected = card.querySelector("input:checked");
            const feedback = card.querySelector(".feedback");

            card.querySelectorAll(".option").forEach((el, index) => {
                el.classList.toggle("correct", index === correctIndex);
                el.classList.toggle(
                    "wrong",
                    Boolean(selected) && index === Number(selected.value) && index !== correctIndex
                );
            });

            if (!selected) {
                feedback.textContent = "Choose an option first.";
                return;
            }

            if (Number(selected.value) === correctIndex) {
                feedback.textContent = "✓ Correct!";
            } else {
                feedback.textContent = `✗ Not quite. ${qExplanation(card, data, correctIndex)}`;
            }
        });
    });
}

function qExplanation(card, data, correctIndex) {
    const index = [...document.querySelectorAll(".quiz-question")].indexOf(card);
    return data.questions[index]?.explanation || `The correct option is ${correctIndex + 1}.`;
}

function renderLearningPath(data) {
    const levels = data.levels || [];
    resultEl.innerHTML = `
        <p class="answer">${escapeHtml(data.overview || "")}</p>
        <div class="level-grid">
            ${levels.map(level => `
                <section class="level">
                    <h3>${escapeHtml(level.level)}</h3>
                    <div class="duration">${escapeHtml(level.duration)}</div>
                    <ul>
                        ${(level.topics || []).map(t => `<li>${escapeHtml(t)}</li>`).join("")}
                    </ul>
                    ${level.resources?.length ? `
                        <strong>Resources</strong>
                        <ul>${level.resources.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
                    ` : ""}
                </section>
            `).join("")}
        </div>
        ${(data.practice_projects || []).length ? `
            <div class="practice">
                <strong>Practice projects</strong>
                <ul>${data.practice_projects.map(p => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
            </div>
        ` : ""}
    `;
}

async function submitTask() {
    const task = taskEl.value;
    const value = inputEl.value.trim();

    if (!value) {
        setStatus("Please enter some content first.", true);
        inputEl.focus();
        return;
    }

    const endpoints = {
        qa: "/qa",
        explain: "/explain",
        quiz: "/quiz",
        summarize: "/summarize",
        learn: "/learn/recommendations"
    };

    const payload = task === "qa"
        ? { question: value }
        : task === "explain" || task === "learn"
            ? { topic: value }
            : { text: value };

    submitBtn.disabled = true;
    clearBtn.disabled = true;
    setStatus("EduGenie is thinking...");
    resultCard.classList.remove("hidden");
    resultEl.innerHTML = "";

    try {
        const response = await fetch(endpoints[task], {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed.");
        }

        if (task === "qa") renderText(data.answer);
        else if (task === "explain") renderText(data.explanation, "explanation");
        else if (task === "summarize") renderText(data.summary, "summary");
        else if (task === "quiz") renderQuiz(data);
        else if (task === "learn") renderLearningPath(data);

        setStatus("Done.");
    } catch (error) {
        resultEl.innerHTML = "";
        setStatus(error.message, true);
    } finally {
        submitBtn.disabled = false;
        clearBtn.disabled = false;
    }
}

taskEl.addEventListener("change", setTaskUI);
submitBtn.addEventListener("click", submitTask);
inputEl.addEventListener("keydown", event => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        submitTask();
    }
});

clearBtn.addEventListener("click", () => {
    inputEl.value = "";
    resultEl.innerHTML = "";
    resultCard.classList.add("hidden");
    setStatus("");
});

copyBtn.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(resultEl.innerText);
        setStatus("Result copied to clipboard.");
    } catch {
        setStatus("Could not copy the result.", true);
    }
});

setTaskUI();
