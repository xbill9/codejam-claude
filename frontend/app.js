/**
 * Resume Tailor — Frontend Client Application
 */

const SAMPLE_JOB = `Senior Backend Engineer — Cloud Services
Responsibilities:
- Design and scale distributed microservices handling 50k+ requests/sec using Python, FastAPI, and PostgreSQL.
- Optimize database performance, indexing, and complex queries to achieve sub-50ms p95 latency.
- Implement secure authentication and authorization protocols (OAuth2/OIDC) across public and internal APIs.
- Collaborate with platform and DevOps teams on CI/CD pipelines, Docker containerization, and automated testing.`;

const SAMPLE_RESUME = `• Built backend APIs in Python for user authentication and authorization
• Managed database migrations and worked on optimizing query performance
• Worked with DevOps to setup Docker containers and GitHub Actions CI pipelines
• Improved server uptime and resolved production incidents during on-call rotation`;

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const jobInput = document.getElementById("job-desc-input");
  const resumeInput = document.getElementById("resume-input");
  const jobCharCount = document.getElementById("job-char-count");
  const resumeCharCount = document.getElementById("resume-char-count");
  const btnTailor = document.getElementById("btn-tailor");
  const btnSample = document.getElementById("btn-sample");
  const btnCopyAll = document.getElementById("btn-copy-all");
  const loadingState = document.getElementById("loading-state");
  const resultsSection = document.getElementById("results-section");
  const cardsContainer = document.getElementById("cards-container");
  const resultsCount = document.getElementById("results-count");
  const roleSummaryBadge = document.getElementById("role-summary-badge");
  const errorBanner = document.getElementById("error-banner");
  const errorMessage = document.getElementById("error-message");
  const errorDismiss = document.getElementById("error-dismiss");
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toast-message");

  let currentTailoredBullets = [];

  // Input Validation & Character Counting
  function updateValidation() {
    const jobLen = jobInput.value.trim().length;
    const resumeLen = resumeInput.value.trim().length;

    jobCharCount.textContent = `${jobInput.value.length.toLocaleString()} / 15,000`;
    resumeCharCount.textContent = `${resumeInput.value.length.toLocaleString()} / 15,000`;

    const isValid = jobLen >= 20 && resumeLen >= 10 && jobInput.value.length <= 15000 && resumeInput.value.length <= 15000;
    btnTailor.disabled = !isValid;
  }

  jobInput.addEventListener("input", updateValidation);
  resumeInput.addEventListener("input", updateValidation);

  // Keyboard shortcut: Cmd/Ctrl + Enter to trigger
  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      if (!btnTailor.disabled) {
        btnTailor.click();
      }
    }
  });

  // Try with Sample Data
  btnSample.addEventListener("click", () => {
    jobInput.value = SAMPLE_JOB;
    resumeInput.value = SAMPLE_RESUME;
    hideError();
    updateValidation();
    jobInput.focus();
  });

  // Error Banner handling
  function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
    errorMessage.textContent = "";
  }

  errorDismiss.addEventListener("click", hideError);

  // Toast Notification
  let toastTimer = null;
  function showToast(msg) {
    if (toastTimer) clearTimeout(toastTimer);
    toastMessage.textContent = msg;
    toast.classList.remove("hidden");
    toastTimer = setTimeout(() => {
      toast.classList.add("hidden");
    }, 2500);
  }

  // Clipboard copy helper with fallback
  async function copyToClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {
      // Fall through to fallback
    }

    try {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const successful = document.execCommand("copy");
      document.body.removeChild(textarea);
      return successful;
    } catch (err) {
      console.error("Clipboard copy failed", err);
      return false;
    }
  }

  // Render Comparison Cards
  function renderCards(bullets) {
    cardsContainer.innerHTML = "";
    currentTailoredBullets = bullets;

    bullets.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "diff-card";

      // Left Column: Original
      const origCol = document.createElement("div");
      origCol.className = "diff-original";
      origCol.innerHTML = `
        <div class="diff-header">
          <span class="diff-tag-muted">Original Bullet #${index + 1}</span>
        </div>
        <p class="diff-original-text">${escapeHtml(item.original)}</p>
      `;

      // Right Column: Tailored
      const tailoredCol = document.createElement("div");
      tailoredCol.className = "diff-tailored";
      tailoredCol.innerHTML = `
        <div class="diff-header">
          <div class="diff-tags">
            <span class="tag-verb">${escapeHtml(item.action_verb || "Action")}</span>
            <span class="tag-metric">${escapeHtml(item.impact_metric || "Impact")}</span>
            <span class="tag-skill">${escapeHtml(item.key_skill || "Skill")}</span>
          </div>
        </div>
        <p class="diff-tailored-text">${escapeHtml(item.tailored)}</p>
        <div class="diff-card-footer">
          <button class="btn-copy-card" data-index="${index}">
            📋 Copy Bullet
          </button>
        </div>
      `;

      card.appendChild(origCol);
      card.appendChild(tailoredCol);
      cardsContainer.appendChild(card);
    });

    // Attach copy handlers to individual card buttons
    document.querySelectorAll(".btn-copy-card").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const idx = parseInt(btn.getAttribute("data-index"), 10);
        const bulletText = currentTailoredBullets[idx]?.tailored || "";
        const copied = await copyToClipboard(bulletText);
        if (copied) {
          const originalText = btn.textContent;
          btn.textContent = "✓ Copied!";
          btn.classList.add("copied");
          setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove("copied");
          }, 2000);
        }
      });
    });
  }

  // Copy All Bullets
  btnCopyAll.addEventListener("click", async () => {
    if (!currentTailoredBullets.length) return;
    const formatted = currentTailoredBullets
      .map((b) => `• ${b.tailored}`)
      .join("\n\n");
    const copied = await copyToClipboard(formatted);
    if (copied) {
      showToast("All tailored bullets copied to clipboard!");
    }
  });

  // Handle Form Submission / API Call
  btnTailor.addEventListener("click", async () => {
    hideError();
    const jobText = jobInput.value.trim();
    const resumeText = resumeInput.value.trim();

    if (!jobText || !resumeText) {
      showError("Please enter both target job description and current resume text.");
      return;
    }

    // Enter loading state
    btnTailor.disabled = true;
    jobInput.disabled = true;
    resumeInput.disabled = true;
    loadingState.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    try {
      const response = await fetch("/api/tailor", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobText,
          resume_text: resumeText,
        }),
      });

      if (!response.ok) {
        let errorDetail = "Failed to tailor bullets.";
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errorDetail;
        } catch (_) {}
        throw new Error(errorDetail);
      }

      const data = await response.json();

      if (!data.bullets || !data.bullets.length) {
        throw new Error("No bullets could be generated from the given input.");
      }

      // Update results UI
      roleSummaryBadge.textContent = data.role_summary || "Aligned to Job";
      resultsCount.textContent = `${data.bullets.length} ${data.bullets.length === 1 ? "Bullet" : "Bullets"} Elevated`;
      renderCards(data.bullets);

      resultsSection.classList.remove("hidden");
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      showError(err.message || "An unexpected error occurred while contacting the server.");
    } finally {
      loadingState.classList.add("hidden");
      jobInput.disabled = false;
      resumeInput.disabled = false;
      updateValidation();
    }
  });

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initial validation check
  updateValidation();
});
