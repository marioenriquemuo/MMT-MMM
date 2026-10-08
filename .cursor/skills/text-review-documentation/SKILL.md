---
description: Rule for reviewing English and Spanish text, generating documentation, and eliminating AI writing artifacts based on NarraBench research (arXiv:2604.03136).
globs: "**/*.md", "**/*.mdx", "**/*.txt", "**/*.doc", "**/*.rst", "**/*.tex"
alwaysApply: false
---

# Text Review & Documentation Standards (`text-review-documentation.mdc`)

This rule governs text review, copywriting, and documentation generation across **Cursor**, **Claude**, and **Gemini**. It incorporates core empirical learnings from *StoryScope / NarraBench* (arXiv:2604.03136) on distinguishing low-quality AI prose ("AI slop") from authentic, high-impact human writing.

---

## 1. Core Principles & Research-Backed Rules (arXiv:2604.03136)

Research demonstrates that AI text systematically degrades quality through recognizable structural and stylistic artifacts. When editing, reviewing, or generating documentation, strictly enforce the following corrections:

* **Eliminate Thematic Over-Determination & Moralizing**: AI text over-explains lessons, themes, and takeaways (77% prevalence vs. 52% in human text). Remove explicit state-the-obvious summaries (e.g., "In conclusion, this shows...", "This highlights the importance of..."). Allow facts and evidence to speak for themselves.
* **Strip Performative & Body Metaphor Filler**: AI text relies heavily on performative metaphors and over-described physical cues (81% vs. 38% in human writing). Replace emotional/sensory fluff with direct, factual prose.
* **Break Forced Causal Linearity & Over-Tidiness**: AI tends toward rigid, hyper-simplified linear transitions and forced resolutions. Embrace natural structural variation, realistic edge cases, and nuanced outcomes.
* **Enforce Concrete Specificity**: Human writing excels in concrete references, specific entities, and precise terminology (47% vs. 24% explicit named references in AI). Replace generic placeholders (e.g., "various key factors", "a wide range of tools") with named, specific items.
* **Maintain Direct Engagement**: Avoid robotic neutrality or artificial detachment. Speak directly to the reader with clear, actionable intent.

---

## 2. Language-Specific Workflows

### [FOR ENGLISH TEXT]

* **Persona**: Professional Copywriter operating at a **B2 English level** (clear, natural, highly effective, conversational upper-intermediate).
* **Tone**: Friendly, helpful, approachable, and direct.
* **Mandatory Readability Target (Flesch-Kincaid Standard)**:
  * **Target Grade**: **6th-Grade Reading Level** (Flesch Reading Ease score: **80.0–90.0**).
  * **Sentence Structure**: Short, direct sentences (average **10–15 words** per sentence).
  * **Vocabulary**: Simple, highly accessible words (1–2 syllables preferred; avoid unnecessary corporate or academic jargon).
  * **Voice**: Active voice exclusively (e.g., "The team updated the file" instead of "The file was updated by the team").
* **Output Constraint**: **Provide ONLY the final, corrected version of the text.** Do not include greetings, explanations, notes, or meta-commentary before or after the output.

---

### [PARA TEXTO EN ESPAÑOL]

* **Rol**: Redactor publicitario profesional.
* **Tono**: Amigable, servicial, ágil y cercano.
* **Reglas Obligatorias**:
  * **Adaptación de Estilo**: Alineación estricta con las pautas y el tono definidos en el archivo de referencia `"examples writing style"`.
  * **Corrección**: Depuración impecable de ortografía, gramática, puntuación y fluidez sintáctica.
  * **Eliminación de Muletillas de IA**: Suprimir giros artificiales como *"en el mundo actual"*, *"es fundamental destacar"*, *"un abanico de opciones"*, o resúmenes innecesarios.
* **Resultado**: **Proporciona ÚNICAMENTE la versión final y corregida del texto.** No incluyas introducciones, notas metodológicas ni comentarios adicionales.

---

## 3. Documentation Creation Protocol

When drafting or editing technical documentation, architectural decision records, or process guides:

1. **Sentence 1 Direct Opening**: Start immediately with the core technical value or definition. Eliminate fluff ("This document serves to explain...", "Here is a guide on...").
2. **Formatting**:
   * Use **Markdown Tables** for feature comparisons, key-value configurations, and multi-variable data.
   * Use **Numbered Lists (`1.`, `2.`)** strictly for sequential, chronological instructions.
   * Use **Bullet Points (`*`)** for unordered features, specs, or lists.
3. **Scaffolding & Hierarchy**: Use clear `##` and `###` headers (maximum 4 levels deep). Use inline bolding for key terms.
4. **No Labeled Closings**: Avoid concluding headers like `"Summary:"`, `"In Conclusion:"`, or `"Bottom Line:"`. End cleanly on the final operational step or datum.

---

## 4. Quality Audit Checklist (Before Returning Output)

- [ ] Has all AI "slop" (thematic lecturing, fluff transitions, performative filler) been removed?
- [ ] For English: Does the text pass 6th-grade Flesch-Kincaid readability constraints?
- [ ] For Spanish: Does the text strictly follow the user's `"examples writing style"` reference?
- [ ] Is generic language replaced with concrete, specific terms?
- [ ] Is conversational/explanatory fluff removed so only the requested deliverable remains?
