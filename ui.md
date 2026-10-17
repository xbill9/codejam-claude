# Resume Tailor — UX Design Doc

**Designer:** TBD  
**Status:** Draft v0.1  
**Last updated:** 2026-10-16  

---

## 1. The design bet

We are betting that seeing the immediate, side-by-side contrast between a candidate's original rough bullet and an executive-grade XYZ revision (the "Before → After Impact Diff") creates instant relief and trust. We are investing 80% of our visual and interaction design into the comparison cards, while keeping the dual-input area completely invisible and friction-free.

## 2. The defining interaction

User pastes their text and taps **"Tailor Bullets"**. The button depresses with a subtle pulse, and a clean microcopy label appears: *"Elevating bullets to Google XYZ format..."*. Within ~3 seconds, the screen smoothly auto-scrolls down as the output feed renders a series of high-contrast comparison cards with a 50ms stagger. On each card, the original bullet sits in muted slate, while the tailored bullet shines in crisp, dark typography with the power action verb highlighted and quantifiable impact framed. The user taps **"Copy"** on the first card—the icon instantly flips to a green checkmark reading *"Copied!"*. Total elapsed time: ~4 seconds. It feels like having an elite executive resume coach standing over your shoulder and polishing your rough draft into pure gold.

## 3. Screen inventory

The product consists of a single responsive web workspace:

- **Resume Tailor Studio (`/`)** — A single-page, dual-section workspace containing the dual input panels (Job Posting + Current Bullets) and the dynamic Results stream (Comparison Cards + Batch Action Toolbar).

No sub-pages, no tabs, no modal dialogues.

## 4. Screen-by-screen specs

### Resume Tailor Studio

**Purpose:** Provide a clean, frictionless interface to paste job and resume text, trigger the AI transformation, and evaluate/copy upgraded bullets in one view.

**Layout (top to bottom):**
1. **Header Bar:** Clean brand wordmark ("Resume Tailor") + one-line subtext (*"Upgrade rough bullets into high-impact Google XYZ accomplishments"*).
2. **Dual Input Area (side-by-side on desktop ≥768px, stacked on mobile):**
   - *Left Pane*: "Target Job Description" textarea with clear placeholder (*"Paste the role requirements, responsibilities, or target job posting..."*).
   - *Right Pane*: "Current Resume Bullets" textarea with clear placeholder (*"Paste 3–8 rough bullets or experience lines from your resume..."*).
3. **Action Bar:**
   - Centered primary button: **"Tailor Bullets"** (styled in bold primary indigo/black with clear hover/active states).
   - Secondary text action: *"Try with sample data"* (instantly loads realistic sample job description and resume bullets for 1-click evaluation).
4. **Results Feed (appears dynamically below action bar):**
   - *Toolbar*: Results counter badge (*"5 Bullets Tailored"*) + primary action button **"Copy All Bullets"**.
   - *Comparison Card Stream*: Vertical stack of structured cards, each split into:
     - *Original Column (40% width)*: Muted background, neutral text, labeled *"Original"*.
     - *Tailored Column (60% width)*: Crisp white background, subtle border, power action verb tagged in bold, metric highlight badge, and a dedicated *"Copy"* button.

**Key interactions:**
- **Text Entry:** Button automatically enables when both text areas contain meaningful input (≥10 characters each).
- **Click "Try with sample data":** Pre-fills both text boxes with realistic inputs and enables the primary button immediately.
- **Click "Tailor Bullets":** Primary button transitions to disabled loading state with a spinner; inputs are locked to prevent edits during flight; view smoothly scrolls to results container.
- **Click "Copy" on a Card:** Copies the tailored bullet to the system clipboard; button text changes to *"Copied!"* with a green check icon for 2 seconds.
- **Click "Copy All Bullets":** Formats all tailored bullets with bullet points (`• `) and newline separators, copies to clipboard, and shows a transient floating toast (*"All bullets copied to clipboard"*).

**States:**
- **Default / First-time:** Inputs are blank with clear placeholder prompts. The "Try with sample data" button is prominent. The results container is hidden.
- **Loading:** Button disabled with an animated spinner and label *"Tailoring bullets... (~3s)"*. Input fields are dimmed (opacity 0.7) and read-only.
- **Error:** Clean dismissible alert banner appears directly above the action button with plain English copy (*"Unable to tailor bullets: Connection timed out. Your inputs have been preserved. Please try again."*).
- **Edge / "Too much":** Character counter warns in amber if pasted text exceeds 12,000 characters per box, preventing prompt truncation.

## 5. The user journey

The user opens the app on their laptop with their resume document in an adjacent window. They see the two side-by-side text boxes. Instead of wondering what format is required, the placeholder text clearly shows how a bullet should look. To test the app first, they click *"Try with sample data"*. The boxes fill with a senior backend role and three generic bullets.

They click **"Tailor Bullets"**. The button shifts to a subtle pulse. Three seconds later, the comparison cards appear below. The user scans the first card: their original bullet (*"Worked on backend APIs for user authentication"*) is paired with an upgraded XYZ bullet (*"Architected and deployed OAuth2 authentication service across 12 microservices, decreasing unauthorized auth attempts by 34% while maintaining sub-50ms latency"*). 

The user says *"Wow, that actually matches the job description's security requirements"*. They click **"Copy"**, switch to their resume doc, and paste it. They clear the sample, paste their real job posting and bullets, and repeat the process.

## 6. Component & visual notes

- **Typography:** Inter or system sans-serif (`system-ui, -apple-system, sans-serif`) for high clarity and editorial polish. Monospace font for metric tokens or formula tags.
- **Color:** Clean monochromatic slate foundation (light gray `#f8fafc` canvas, white `#ffffff` cards, slate `#0f172a` primary text) paired with deep indigo (`#4f46e5`) for actions and emerald green (`#10b981`) for successful copy states.
- **Motion:** 200ms ease-out transitions for buttons and card hover states; subtle 50ms staggered slide-up for generated cards. No distracting physics or bouncing.
- **The signature visual:** The **"XYZ Split-Card"**. Each card clearly delineates the "Before" (light gray background, 14px muted font) and the "After" (white elevated card, 15px high-contrast text, emerald badge highlighting the impact metric and purple badge highlighting the power verb).
- **Microcopy voice:** Confident, executive, concise. 
  - Button: *"Tailor Bullets"*
  - Loading: *"Elevating bullets to XYZ format..."*
  - Badge: *"Impact: Quantifiable Outcome"*

## 7. Accessibility & inclusion

- **Screen readers:** All inputs use explicit `<label>` and `<textarea>` associations. Live regions (`aria-live="polite"`) announce loading state and copy confirmations.
- **Keyboard navigation:** Full tab order flow from Job Description → Current Bullets → Tailor Button → Card Copy Buttons. Keyboard shortcut (`Cmd/Ctrl + Enter`) supported to trigger tailoring from either textarea.
- **Contrast & sizing:** All text elements exceed WCAG AA 4.5:1 contrast ratio. All interactive tap targets are at least 44×44px.
- **Low bandwidth:** The web interface is completely self-contained vanilla HTML/CSS/JS without heavyweight frontend frameworks or large asset downloads.

## 8. What we are NOT designing

- **No settings screens or theme selectors** — a single, well-calibrated clean light mode.
- **No modal popups or confirmation dialogs** — all states and error feedback render inline.
- **No rich-text WYSIWYG editors** — plain text eliminates styling conflicts and copy-paste clipboard glitches.
- **No PDF/DOCX export or layout visualizers** — user pastes directly into their own document workflow.
- **No user account or login screens** — completely stateless and accessible without authentication.

## 9. Open design questions

- [ ] Should the dual input fields auto-collapse into a compact summary once cards are generated on smaller screens to maximize comparison card viewing area?
- [ ] Should each tailored bullet card include an "Undo / Re-roll" single bullet button in v1, or does that add unnecessary complexity?

## 10. Handoff to engineering

The comparison cards require structured data: the backend must return a JSON array where each item provides `original_bullet`, `tailored_bullet`, `action_verb`, and `key_skill`. Response latency must strictly stay under 4 seconds end-to-end to maintain the fluid "instant upgrade" feeling.
