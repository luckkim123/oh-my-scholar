# Writing-Craft Card — Argumentation & Narration Rules (FLOW·TONE·LOGIC·STRUCTURE)

> oms's writing-craft SSOT. scholar-drafter (generation), scholar-inspector (prose/logic critique), and scholar-verifier (§7 WARN detection) *reference* this card. **No duplicate embedding — do not re-list the rules in each agent; always point to this file** (drift prevention, same discipline as the abstract-WARN precedent).
>
> **Role separation**: `latex.md` = *how to typeset* (compilation, math, `\tag`, section modularization) ⊥ this card = *how to argue & narrate* (flow, tone, logic, structure). The two do not overlap.
>
> Each rule carries a **source anchor**. ⚠️ Source honesty: some of the Gopen-Swan, Schimel, and Pinker rules come via secondary summaries — adopted as *drafter rules* (not as citation claims), so this is fine, but when an oms-produced paper quotes them verbatim, check against the original. citation/.bib is not a promotion target of this card (permanently prohibited).

---

## §1. FLOW — Flow (top priority; the core of "the development feels awkward")

- **old→new (Gopen-Swan, top-level flow rule)**: each sentence starts with information the reader *already knows (old information)* (topic position) and places *new/emphasized information* at the end of the sentence (**stress position**, just before the period or semicolon). When the flow feels awkward, it is almost always a violation of this — new information has come to the head of the sentence, breaking the connection backward. ⚠️ **This rule has *higher priority* than the preference for the active voice***: the passive voice is allowed if needed to put old information first. [Gopen & Swan 1990]
- **subject-verb proximity**: place the verb as soon as possible after the grammatical subject. Do not break up the subject and verb with a long interjected phrase (no buried predicate). [Gopen-Swan]
- **action-in-verb (anti-nominalization)**: do not nominalize the action of a clause; use a verb. `we performed an analysis of`→`we analyzed`, `provides a review of`→`reviews`. [Gopen-Swan / Sainani]
- **context first**: precede a new claim or new term with one sentence of context before demanding it. [Gopen-Swan]
- **banana rule**: repeat key terms (technique names, variables, group names) with the *exact same word*. Do not vary with synonyms — varying makes the reader think it is a new concept. ("Don't call a banana 'an elongated yellow fruit.'") [Sainani]

## §2. TONE — Tone (removing AI slop)

- **no decorative verbs/adjectives (a principle, not a list)**: do not use them if there is no actual meaning payload. Test = "Does this verb/adjective add *content*, or is it *decoration*?". Seed tokens: delve, underscore, showcase, foster, leverage, intricate, pivotal, crucial, comprehensive, meticulous, realm, tapestry, testament, seamless, landscape (in the abstract sense). ⚠️ A static list rots (authors start avoiding 'delve'), so enforce the *principle* and use the list only as §7 detection seeds. [Nature Human Behaviour 2025 — LLM surplus vocabulary 66% verbs / 14% adjectives / humanizer]
- **no copula avoidance**: do not change `is` to `serves as`/`stands as`/`boasts`/`features`. [humanizer]
- **em-dash cap**: the em-dash (`—`) is not a matter of restraint but nearly prohibited — replace it with a period, comma, colon, or parentheses, or restructure the sentence. At most 1-3 per section. [humanizer / anti-ai-slop]
- **no structural slop**: forced rule-of-three, synonym cycling, three consecutive sentences of identical length (vary sentence length), negative parallelism ("It's not just X, it's Y"), `-ing` participle padding. [anti-ai-slop]
- **no significance hype**: a claim about impact is not evidence of impact. Seed phrases: `paves the way for`, `a crucial/pivotal step toward`, `has the potential to revolutionize`, `opens new avenues`, `sheds light on`, `bridges the gap`. Same principle as the decorative-word rule — the phrase is banned when it carries no measured payload, not because the words are forbidden. [humanizer]
- **no formulaic opener**: `In recent years, X has attracted increasing attention` / `With the rapid development of ...`. An opening sentence that would fit any paper in the field says nothing about this one. [humanizer]

## §2.5 PRESERVE — What §2 must not touch (over-correction guard)

§2 pushes in one direction only: remove. Without a guard on the other side, a
revise loop converges on stripping things that are *correct academic writing*,
and the result reads cleaner while saying something false. Everything here is
exempt from §2 and from §7 detection.

- **Evidence-tied hedging is correct and required.** `suggests` · `is consistent with` ·
  `we hypothesize that` · `may indicate` · `appears to` stay whenever the claim is
  genuinely uncertain. Turning *"the results suggest X"* into *"the results prove X"*
  does not remove AI slop — it **manufactures over-claiming**, which §3 then has to
  catch. §2.9's target is hedging-by-vagueness (`somewhat`, `to some extent`), which is
  hedging with no referent; calibrated hedging has one.
- **Passive voice is fine when the actor is irrelevant** — *"Samples were normalized to
  total protein."* Rewriting for an agent that does not matter adds a false subject.
- **First-person plural `we` is standard.** Do not rewrite to avoid it.
- **Definitions, named methods and metrics, technical terms, equations, and symbols stay
  verbatim.** A synonym swap here is not a style edit, it is a terminology change — and
  it is exactly what tortured-phrase screening flags in suspect papers.
- **Never invent, drop, or alter a number, an equation, or a citation key.** A rewrite
  preserves every `\cite{...}` and every reported value unchanged.
- **Coverage is preserved.** If the original had five paragraphs, so does the rewrite.
  A shorter document is not evidence of a better one.

⚠️ **This section is why writing detection is WARN, not FAIL** (see §7). Every rule in
§2 has a legitimate exception living here, so a hard gate on §2 would block correct
prose. Detect, list, and let a human confirm.

## §3. LOGIC — Argument Construction

- **one ping**: one paper = one sharp idea, stated **explicitly** in the body ("The main idea of this paper is…"). Do not make the reader guess. If there are several ideas, that means several papers. [Peyton Jones]
- **refutable contribution bullets**: put contributions before the Intro as **refutable bullets**. NOT "We describe a cool system"; YES "We prove X (Section 4)". This bullet list drives the whole paper. State the problem with examples, not grand claims (molehills not mountains). [Peyton Jones]
- **forward-reference**: each contribution bullet forward-references its evidence (Section X). ⚠️ "The rest of this paper is structured as follows…" is prohibited — the forward-references in the contribution bullets take over that role. [Peyton Jones]
- **TEEL paragraph**: a body paragraph = Topic sentence (point first) → Evidence (data, citations) → Explanation (interpretation) → Link (to the next thesis). [academic-research-skills]
- **claim ↔ own evidence (the results-section counterpart of overgeneralization)**: every empirical claim about *our* method carries (a) an anchor — a `\ref{tab:...}`, a `\ref{fig:...}`, or a reported number — and (b) a verb no stronger than that anchor supports. This is a different axis from claim↔citation (verifier's claim-faithfulness), which only inspects sentences carrying a `\cite`. Results-section over-claiming lives in the sentences that carry none, so nothing was watching them.
  - *unbacked claim* → add the anchor or soften. NOT "Our method is more robust"; YES "Accuracy drops by 2 points under distribution shift versus 11 for the baseline (Fig. 3)."
  - *verb stronger than anchor* → downgrade. `demonstrate`/`prove`/`establish`/`confirm`/`guarantee` off a single experiment is over-claiming: NOT "This demonstrates universal superiority"; YES "On these three datasets, our method matches or exceeds the strongest baseline (Table 2)."
  - *vague magnitude* → a number, and prefer a **range** (`2--6%`) over one averaged value unless the averaging is stated. Attribute each number to its method, metric, and baseline, and lead the comparison with the strongest competitor, not the weakest.
  - ⚠️ This rule does not license removing hedging — §2.5 governs there. A calibrated verb over a weak anchor is the *correct* outcome, not a defect.
- **overgeneralization warning — the top failure mode**: a claim broader than its citation basis is the LLM's #1 hallucination (empirically 51%, more common than invented papers). Match the breadth of a claim to the breadth of its basis. [AutoSurvey error taxonomy]
- **additional LLM academic-writing failure modes (traps the drafter falls into)**: among the externally documented failure modes, beyond the overgeneralization above, watch out separately for — ① **numeric hallucination** (plausible but source-data-inconsistent statistics/numbers) → cross-check every quantitative claim against the results notes ② **method generalization** (describing a standard method instead of the concrete implementation) → the method section writes the actual implementation of *this* system. (③ term confusion = treating related terms interchangeably is the flip side of §1 banana rule — goes there.) ⚠️ Blog source (adopted as drafter rule, not a citation claim — see §source honesty). [manuelcorpas 2026-01 / global wiki reference]

## §4. STRUCTURE — Paper & Section Structure

- **CARS 3-move (mandatory Intro skeleton)**: Move 1 establish territory → **Move 2 establish niche/gap** → Move 3 occupy the niche (purpose, contributions, structure). ⚠️ **Never skip Move 2 (the gap)** — stating only the topic (territory) without naming the gap is the #1 reason for rejection. funnel = the formalization of CARS (general area → narrowing gap → the concrete current study). [Swales CARS]
- **OCAR arc**: Opening → Challenge → Action → Resolution is the basic journal arc. Each level (paper, section, paragraph) has its own arc (nested). A broad audience (Nature/Science) uses LD/LDR (front-loading the core) — the arc is chosen by reader patience. [Schimel]
- **hourglass width match**: the Opening (Intro opening width) and the Resolution (Conclusion/Discussion width) must match — a mismatch signals overpromising/underdelivering. The Discussion is the mirror of the Intro (reverse funnel: concrete results → broad implications). [Schimel]
- ⚠️ **venue variation (no hardcoding)**: the related-work position (Peyton Jones "at the end" ↔ CARS/journal "at the front") and the arc choice (OCAR↔LD) are parameterized by the venue card — do not hardcode one approach. (*Orthogonal* to the scale axis of the planner's `<Structure_Types>` — this card is the rhetorical-structure axis.)

## §5. VOICE/VENUE — Voice/venue

- **voice priority**: discipline norms (hard) > journal conventions (strong) > personal style (soft). Discipline norms > journal conventions > personal style. An author's voice cannot override discipline norms. [academic-research-skills]
- **voice choice**: in STEM papers, the passive voice is allowed for describing the method, while the *contribution narration uses the active voice*. (But §1 old→new takes precedence — the passive is allowed for the sake of flow.) [academic-research-skills]

## §6. EXEMPLAR — Style Imitation

- **~5 random representative paragraphs**: inject ~5 actual paragraphs from the target venue/author as verbatim exemplars into the prompt. ⚠️ **No similarity-curated selection (empirically counterproductive) — a *random representative* sample**. Do not exceed ~5 (plateau). **Embedding/embedding search permanently prohibited** (consistent with oms anti-embedding). Supplied via the `voice`/`exemplars` fields of venues.md. [EMNLP 2025 style-imitation; introduction few-shot also re-confirmed to plateau after 3-shot — arXiv:2508.14273 (self-verified)]

## §7. Machine-Check Tokens (verifier WARN detection SSOT)

> The verifier reads these tokens and detects them as **WARN** (not FAIL — treated the same as venue variation, the abstract-WARN precedent). Do not re-list the tokens in the verifier/tests; follow this place as the SSOT.

Detection tokens (1 or more = WARN, 0 = PASS):
- **decorative words**: the §2 seed list (`delve`·`underscore`·`showcase`·`foster`·`leverage`·`intricate`·`pivotal`·`crucial`·`comprehensive`·`meticulous`·`realm`·`tapestry`·`testament`) — word-boundary matching. ⚠️ Since it is WARN, over-detection is allowed (one contextually justified `crucial` gets human confirmation).
- **em-dash**: number of occurrences of Unicode `—` (U+2014) / `–` (U+2013) > 3 per section = WARN.
- **rule-of-three**: a comma-bound 3-item parallel repeats within one paragraph (a cluster of `A, B, and C` patterns) — heuristic, WARN.
- **negative parallelism**: a cluster of `not just .* but` / `not only .* but also` — WARN.

⚠️ **multibyte grep false-negative (confirmed trap)**: multibyte glyphs such as the em-dash (`—`), `×`, `§`, `≤` produce false 0-counts in C-locale `grep`/`grep -P`. **Confirm a residual 0 count only with the Python `re` module** (do not trust `LC_ALL=C grep` alone). abstract-WARN (latex.md §3) follows the same caveat.

---

## Non-goals (deliberately not done)

- **embedding-based exemplar search** — violates the oms anti-embedding principle + EMNLP 2025 empirically shows similarity-curated selection is counterproductive. Replaced by §6 random representatives.
- **Manchester phrasebank text bulk-copy** — IP. Borrow only the taxonomy (move×function); write/cite examples yourself.
- **auto hard-FAIL of writing rules** — static blocklist rot + multibyte false-negative risk. Writing detection only as WARN/formative, not auto-FAIL.
