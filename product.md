# Resume Tailor — Product Design Doc

**Author:** TBD  
**Status:** Draft v0.1  
**Last updated:** 2026-10-16  
**One-liner:** Paste your resume and a job description to get instant, punchy, metric-driven bullets that beat what you'd write yourself.

---

## 1. The user & the moment

- **Who:** A qualified job seeker staring at an open job listing they are genuinely excited about, exhausted by the tedious chore of tailoring resume bullets by hand.
- **When:** It is 9:30 PM on a weeknight. They found an ideal role closing soon. They have their master resume doc open on one side of their screen and the job requirements on the other, paralyzed trying to rephrase vague responsibilities into high-impact accomplishments.
- **Why now:** Generic resumes get filtered out or ignored in seconds. Candidates know every application must be tailored to the job's specific keywords and priorities, but doing it manually takes 45 minutes per application and feels like draining homework.

## 2. The contract (I/O)

- **Input:** Two plain text boxes:
  1. *Job Posting*: Raw pasted text of the target role, responsibilities, and requirements.
  2. *Current Resume*: Raw pasted text of existing bullet points or job experience.
- **Output:** A structured list of tailored resume bullets. Each original bullet is paired with an upgraded revision following the XYZ impact formula (*"Accomplished [X], as measured by [Y], by doing [Z]"*), highlighting aligned keywords, strong action verbs, and quantifiable impact.
- **The loop:** One-shot transformation per job application: Open app → Paste job posting → Paste current bullets → Click "Tailor Bullets" → Review upgraded bullets side-by-side → Click "Copy All" into resume.

## 3. The magical moment

> "Holy cow, it took my generic 'helped build backend endpoints' bullet and turned it into an executive-ready accomplishment that directly highlights this role's exact tech stack."

## 4. Scope: what we ARE building (v1)

- Two side-by-side or stacked text input boxes (Job Posting + Current Resume) with clean placeholders and clear instructions.
- A single prominent action button ("Tailor Bullets") with immediate, responsive loading feedback during generation.
- A side-by-side Before/After comparison card view showing the user's original bullet next to the tailored XYZ version.
- Visual tags on each tailored bullet highlighting the primary skill or competency addressed and the power action verb used.
- One-click clipboard copy buttons: per-bullet "Copy" and a global "Copy All Tailored Bullets" button.

## 5. Scope: what we are NOT building

- **No PDF or DOCX file upload or parsing** — raw plain-text copy-paste avoids parser failures, multi-column layout glitches, and bloated parsing dependencies.
- **No full resume document generation or layout formatting** — this is a bullet-point upgrade tool, not a full resume template or ATS typesetting engine.
- **No user authentication, login, or accounts** — zero signup friction; completely stateless session-based tool.
- **No persistent database or saved history** — avoids privacy, retention, and security liabilities for sensitive employment histories, keeping infrastructure simple.
- **No cover letter or interview prep generation** — prevents scope sprawl; we focus 100% of the experience on the single highest-leverage asset.
- **No job board scraping or URL fetching** — pasting text directly bypasses anti-bot obstacles, paywalls, and brittle web scrapers.

## 6. The signature detail

The **"Before → After Impact Diff"**. Rather than just dumping a wall of new text, each output card contrasts the user's original raw bullet in muted gray against the newly minted bullet in crisp, high-contrast typography with the active verb highlighted and an "XYZ formula" badge. It immediately proves *why* the new bullet is strictly superior without obscuring the candidate's authentic background.

## 7. Success: how we know it worked

- **Primary:** ≥60% of generated sessions result in the user clicking "Copy" or "Copy All" within 60 seconds of generation.
- **Secondary (optional, max 2):**
  - Median generation latency under 4 seconds from click to card render.
- **What we're NOT measuring:** Total user signups, 30-day retention, or session duration (job hunting is episodic; fast task completion is the victory).

## 8. Open questions

- [ ] What is the ideal upper limit on input bullets (e.g., 6–10 bullets) to keep latency under 4 seconds while preserving prompt focus?
- [ ] When an original bullet lacks metrics, should the model insert explicit brackets for numbers like `[by 25% / $X]` or propose plausible benchmark estimates?

## 9. Handoff

- **For UX:** The before-and-after comparison cards must feel clean and celebratory—the user needs to immediately recognize their own work elevated, not unrecognizable AI fluff.
- **For Eng:** End-to-end response time must remain under 4 seconds for up to 8 bullets, using structured JSON output from Gemini to power the side-by-side card rendering without fragile regex parsing.
