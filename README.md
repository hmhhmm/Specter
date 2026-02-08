# Specter.AI - Sentient Mystery Shoppers for QA

> **Live Demo:** [https://specter-green.vercel.app/](https://specter-green.vercel.app/)  
> _(Note: The Vercel deployment above serves the high-fidelity Frontend experience. The Vision-based Ghost Engine backend is not yet publicly hosted, as real-time browser automation requires persistent Node.js environments and dedicated system-level dependencies that exceed standard serverless deployment capabilities.)_

## 👻 Vision

Specter.AI replaces brittle, rigid testing scripts with **"Sentient Mystery Shoppers."**

Traditional QA tests for _code existence_ (is this button in the DOM?). Specter tests for **Human Impact** (can a tech-illiterate senior actually see and click this button?). By combining **Multimodal AI (Vision)** with autonomous browser navigation, Specter detects "Financial Anxiety" bugs—silent killers of conversion like z-index collisions, layout shifts, and accessibility failures that traditional logs never catch.

---

## 🚀 Key Features

### 1. The Specter Lab (Real-time Vision)

Points an autonomous agent at any URL with a natural language objective. Watch the **Neural Link** as the AI "thinks" and "sees" through emulated devices, detecting friction points in real-time using its Glass Layer architecture.

### 2. Incident Vault (Evidence Repo)

A high-fidelity repository of detected regressions. Each incident includes:

- **Digital Twin Blueprints:** Technical X-ray visualizations of the visual failure.
- **Neural Monologue:** The AI's internal reasoning for why this bug causes churn.
- **Revenue Leak Impact:** Data-driven quantification of the financial risk.

### 3. Command Center (Autonomous Remediation)

The "Grand Finale" where detected bugs are quantified into a **Projected Annual Revenue Leak**. Specter doesn't just find bugs; it autonomously drafts and proposes **GitHub Pull Requests** to fix them.

---

## 🛠️ Technical Stack

- **Frontend:** Next.js 16 (App Router), Tailwind CSS 4, Framer Motion
- **UI Components:** Kokonut UI, Shadcn UI, PromptKit
- **Agentic Core:** Playwright v1.58, Stagehand, GPT-4o-Vision
- **Runtime:** Node.js v24 (LTS)

---

## 🏗️ Project Architecture: The "Glass Layer"

To ensure zero DOM pollution during analysis, Specter uses a unique **Glass Layer Architecture**. The target application is loaded in a sandboxed environment, while the AI's annotations, cursor movements, and scanlines are rendered on a transparent overlay. This ensures the demo reflects true external, vision-based analysis exactly as a human would experience it.

---

## 🛠️ Local Development

1. **Install Dependencies:**

   ```bash
   npm install
   ```

2. **Run Dev Server:**

   ```bash
   npm run dev
   ```

3. **Backend Ghost Engine:**
   Requires a dedicated Node environment. See backend folder for more information.
