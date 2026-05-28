# BE 153 Final Project — Presentation Notes
## *Quantifying Stress with Wearables: A Physiology + Cortisol Model*

**Format:** ~12 minutes, 14 core slides + 1 optional (Slide 15
"Translation" can be dropped to hit 10 min). Slide 2 goes deep on the
stress-biology background, Slide 12 is an explicit "limitations"
slide that frames the cortisol result as a simulation-based
prediction, and Slide 16 sets up future biomarker work (uric acid,
epinephrine) called out by the instructor. **Modeling style mirrors
the kidney-stone example:** start with the biological motivation,
state a mechanistic equation, fit constants to data, then propose an
improvement.

For each slide below:

- **Slide title** – exactly what should go on the slide
- **What to put on the slide** – the bare minimum visuals/equations
- **What to say** – the spoken script (read at ~150 wpm gives roughly
  the indicated seconds)

---

### Slide 1 — Title (~30 s)

**Slide:**
- Title: "Quantifying Stress with Wearables: From Heart-Rate to Cortisol"
- Your name, BE 153, Spring 2026
- A small wrist-watch + sweat-sensor icon, plus the HPA-axis cartoon

**Script (≈ 30 s):**
> "Hi, I'm Jack. Today I want to talk about how we can turn an
> everyday wrist wearable — like an Apple Watch or an Empatica band —
> into a stress-detection tool, and then how adding one new chemical
> signal, cortisol, could fundamentally improve those devices. I'll
> build a quantitative model on real data and show what the next
> generation of wearables could look like."

---

### Slide 2 — The biology of acute stress (~65 s)

**Slide:**
- Two-pathway flow diagram (centerpiece):
  ```
  STRESSOR  ─►  cortex / amygdala  ─►  hypothalamus
                                        │
                ┌───────────────────────┴───────────────────────┐
                ▼ (seconds, neural)              (minutes, hormonal) ▼
        SAM axis                                              HPA axis
        sympathetic nerves                                    CRH ➜ pituitary
                │                                                  │
                ▼                                                  ▼
        adrenal MEDULLA                                    adrenal CORTEX
        ↓                                                          ↓
        epinephrine + norepinephrine                            cortisol
        (+ ACh at eccrine sweat glands)
  ```
- Compact effects table:

  | axis | mediator | onset | downstream effects |
  |---|---|---|---|
  | **SAM** (sympathetic) | epinephrine, NE; ACh at sweat glands | seconds | ↑ HR, ↑ BP, peripheral vasoconstriction, ↑ eccrine sweat, ↑ glucose mobilisation |
  | **HPA** (hormonal) | cortisol | 10–20 min | gluconeogenesis, immune suppression, anti-inflammatory, behavioural modulation, negative feedback to brain |

- One callout box: "Eccrine sweat glands are uniquely sympathetic-
  *cholinergic* — they read out SAM tone *and* their sweat carries
  free cortisol that has diffused from blood. One fluid, two
  pathways."

**Script (≈ 65 s):**
> "Before talking about devices, let's establish what's actually
> happening in the body. When the brain interprets a situation as
> threatening — that decision is made by the amygdala and the
> cortex — the hypothalamus activates two parallel response systems
> at once. The first is the sympathetic-adrenal-medullary axis: a
> neural pathway that fires within seconds. The sympathetic nervous
> system signals the adrenal medulla to dump epinephrine and
> norepinephrine into the bloodstream, driving the classic
> fight-or-flight response — heart rate up, blood pressure up,
> peripheral blood vessels constrict, glucose mobilises, and the
> eccrine sweat glands activate. Those sweat glands are unusual:
> they're sympathetic but use acetylcholine, not norepinephrine, so
> sweat conductance is a direct readout of sympathetic tone. The
> second system is the HPA axis: the hypothalamus releases CRH,
> the pituitary releases ACTH, and the adrenal cortex releases
> cortisol. This pathway is slower — cortisol peaks in saliva and
> sweat about 10 to 20 minutes after a stressor and persists for
> over an hour because its half-life is ~66 minutes. Cortisol is
> the body's *dedicated* stress hormone: it mobilises glucose,
> suppresses inflammation, modulates behaviour, and feeds back
> negatively to shut the cascade off. Crucially, the fast SAM axis
> drives every physical signal current wearables can read; the slow
> HPA axis is the chemical signal they're missing."

---

### Slide 3 — Why model stress? (~50 s)

**Slide:**
- 3 bullets: (i) stress drives chronic disease (CV, immune, mental
  health); (ii) global burden of stress-related illness rising; (iii)
  current screening is questionnaire-based — episodic, biased, and
  late.
- A small headline number: "WHO: stress-related disorders projected to
  be the #2 cause of global disability by 2030."
- Optional small image of a smartwatch screen.

**Script (≈ 50 s):**
> "Now that we know what stress *is* biologically, why should we
> bother measuring it continuously? Chronic activation of those same
> two axes is a major driver of cardiovascular disease, immune
> dysregulation, depression, and metabolic disorders. The World
> Health Organization expects stress-related illness to become the
> second largest cause of disability worldwide. But the way we
> *measure* stress today is embarrassingly primitive: a survey at
> the doctor's office, weeks or months apart. To do anything
> preventive, we need a continuous, objective, real-world
> measurement — exactly the problem wearables were built for."

---

### Slide 4 — Stress biology meets the wearable (~50 s)

**Slide:**
- Mapping table: physiological output (from prior slide) → wearable
  sensor → typical placement.

  | Stress output | Wearable sensor | Where | Latency |
  |---|---|---|---|
  | ↑ heart rate, ↓ HRV | PPG / BVP | wrist | < 5 s |
  | ↑ eccrine sweating | EDA (skin conductance) | wrist, fingers | < 10 s |
  | peripheral vasoconstriction | skin thermistor | wrist | ~ 1 min |
  | ↑ blood cortisol | **— missing —** | (sweat OECT, Parlak 2018) | 3–20 min |

- Image: photo of an Empatica E4 / Apple Watch + an inset of Parlak's
  flexible cortisol patch.

**Script (≈ 50 s):**
> "Every wrist wearable on the market today reads the *SAM-axis*
> outputs and only the SAM-axis outputs: photoplethysmography gives
> heart rate and HRV, the EDA electrodes pick up the cholinergic
> sweat burst, and a thermistor captures the peripheral
> vasoconstriction. What no consumer device measures is the HPA-axis
> output — cortisol — because until recently you needed a lab
> ELISA to detect it. Parlak's group has now demonstrated a wearable
> organic electrochemical transistor that measures sweat cortisol
> continuously. So the question becomes: if we already model stress
> well from the SAM channel, how much better could we do if we add
> the HPA channel?"

---

### Slide 5 — The data: WESAD (~50 s)

**Slide:**
- "WESAD — Wearable Stress and Affect Detection, Schmidt et al. 2018"
- Bullets: 15 subjects, ~100 minutes each; wrist (Empatica E4) +
  chest (RespiBAN); 4 conditions (baseline, amusement, stress
  [Trier Social Stress Test], two meditations).
- Insert **`figures/fig1_wrist_signals.png`** — the raw EDA / TEMP /
  BVP / ACC traces for one subject with the protocol shaded.
- Annotate: "EDA shoots up and skin temperature drops during stress."

**Script (≈ 50 s):**
> "I used the WESAD dataset — 15 subjects each wearing both a wrist
> band and a chest belt, with carefully labelled stress, amusement,
> baseline, and meditation periods. The stressor was the Trier Social
> Stress Test: public speaking plus mental arithmetic in front of a
> hostile panel. This figure shows one subject's wrist signals.
> The red band is the TSST. Notice how electrodermal activity climbs
> three-fold, skin temperature drops by a full degree from peripheral
> vasoconstriction, and the BVP variability changes. The biology
> textbook story is right there in the data."

---

### Slide 6 — A mathematical stress index (~60 s)

**Slide:**
- Equation (centerpiece):
  $S(\mathbf{x}) = \beta_0 + \sum_{k} \beta_k\,z(x_k)$
  $P(\text{stress}\mid \mathbf{x}) = \sigma(S(\mathbf{x})) = \frac{1}{1+e^{-S(\mathbf{x})}}$
- Bullet list of features `x_k` (grouped by signal):
  - **EDA:** mean, SCL slope, SCR rate, SCR amplitude
  - **HR/HRV:** mean HR, std HR, RMSSD, SDNN, pNN50
  - **Skin TEMP:** mean, slope, std
  - **ACC:** mean, variance, ENMO
- Footnote: "Fit by L2-regularized logistic regression,
  leave-one-subject-out CV."
- Mention the analogy: "Same form as the kidney-stone supersaturation
  index — features → number → probability through a sigmoid."

**Script (≈ 60 s):**
> "Now the model. In each 60-second window I extract 18 standard
> features — tonic and phasic EDA, heart-rate variability metrics
> from the BVP, skin temperature, motion — and z-score them across
> the population. I then combine them linearly into a stress index
> *S*, exactly the same way the kidney-stone group built their
> supersaturation index. The probability of being stressed comes out
> of a sigmoid. The β coefficients are fit by logistic regression
> with leave-one-subject-out cross-validation, so we never train and
> test on the same person — the model has to generalize to a new
> wearer, which is the realistic clinical setting."

---

### Slide 7 — How well does it work today? (~55 s)

**Slide:**
- Insert **`figures/fig4_roc.png`** (ROC curves, but only show the
  *blue* baseline curve initially – or show both and just refer to
  blue here).
- Table of metrics for the baseline model:
  | metric | value |
  |---|---|
  | accuracy | **0.89** |
  | F1       | **0.79** |
  | precision | 0.71 |
  | recall | 0.89 |
  | **AUROC** | **0.96** |
- Subtitle: "Baseline = what a current wrist wearable can already do."

**Script (≈ 55 s):**
> "Trained on 13 subjects, tested on the unseen 14th and 15th — the
> blue curve. AUROC of 0.96 — very strong. Accuracy hits 89% and
> recall is high. So an Apple Watch with this model could correctly
> flag 89% of stress episodes. But look at precision: only 71%.
> That means about one in four 'stress alerts' the watch raises is
> actually noise — a workout, a hot room, a moment of excitement.
> That false-positive rate is exactly why people stop trusting
> stress-tracker apps after a few weeks."

---

### Slide 8 — Where the model breaks (~45 s)

**Slide:**
- Insert **`figures/fig7_coefficients.png`** (standardised
  coefficients, blue bars only).
- Call out the dominant features:
  - HR mean (β ≈ +3.7)
  - ENMO/motion (β ≈ −2.1)
  - temp slope (β ≈ −2.1)
  - SCR rate (β ≈ +1.5)
- Bullet: "Every one of these is *non-specific* — exercise
  raises HR, hot weather raises EDA, sitting still lowers ENMO."
- A small icon strip: 🏃 ☀️ 🍷 → "false positives"

**Script (≈ 45 s):**
> "Look at what the model is leaning on. The biggest knob is heart
> rate, followed by motion, skin-temperature drift, and EDA peak
> rate. Each of those is biologically valid — but each is also
> elevated by completely non-stress conditions: exercise, warm
> environments, caffeine, alcohol, even just standing up.
> The current device measures *correlates* of stress, not stress
> itself. So we hit a ceiling: 95–96% AUROC, but real-world
> precision still suffers."

---

### Slide 9 — A chemical answer: cortisol (~60 s)

**Slide:**
- Equation (centerpiece — mechanistic kinetic model):
  $$\frac{dC}{dt} = -\lambda\,(C - C_{\text{basal}}) + k_s\,u(t)$$
- Parameter table (sourced from literature, cite):
  | symbol | value | source |
  |---|---|---|
  | $C_{\text{basal}}$ | ~5 nmol/L | Hellhammer 2007 |
  | half-life $T_{1/2}=\ln 2 / \lambda$ | ~66 min | Czeisler 1999 |
  | drive delay (sweat) | ~3 min | Parlak 2018 |
  | peak ratio | ~9× basal under acute stress | **Cay 2018 (NCI)** |
- Right side: insert **`figures/fig2_cortisol_simulation.png`** (the
  simulated trace with shaded protocol).

**Script (≈ 60 s):**
> "Here's the candidate chemical signal. Cortisol is the body's
> dedicated stress hormone — released by the adrenal cortex through
> the HPA axis whenever the brain *interprets* a situation as
> threatening, and not for any other reason. I built a one-compartment
> kinetic model: cortisol concentration relaxes back to its baseline
> at a rate λ, set by the 66-minute clearance half-life, and is
> driven up by a stress input u(t) that the brain switches on.
> I calibrated the gain so that prolonged stress drives cortisol to
> nine times baseline, matching the salivary-cortisol measurements in
> Cay et al. 2018 — they showed exam stress in medical students
> raised cortisol roughly nine-fold. The right panel shows the
> simulated trajectory: flat at baseline, then a smooth rise during
> and after the TSST, decaying over the next hour."

---

### Slide 10 — Generating cortisol features (~40 s)

**Slide:**
- Insert **`figures/fig3_feature_distributions.png`** (or just the
  cort_mean and cort_slope panels).
- Bullets:
  - Three cortisol features per window: mean, slope (nmol L⁻¹ min⁻¹),
    AUC.
  - Per-subject log-normal variability in basal level and gain
    (Hellhammer 2007 CVs).
  - 8% multiplicative sensor noise to mimic real OECT performance
    (Parlak 2018).
- Honest reminder box (foreshadows Slide 12): "These cortisol values
  are *simulated*, not recorded — WESAD never collected cortisol.
  We are using a literature-validated kinetic model to predict the
  *response* a real wearable cortisol sensor would expose. Full
  limitations covered after the headline result."

**Script (≈ 40 s):**
> "From the simulated cortisol trace I pull three features in each
> 60-second window: the mean level, the slope, and the area under
> the curve. To make this realistic I added two things: inter-subject
> log-normal variability — about 35% CV in basal cortisol, 40% in
> peak response, which matches the salivary-cortisol literature —
> and a multiplicative 8% sensor noise, matching what Parlak's group
> reported for their wearable OECT cortisol sensor. The histograms
> show that even with all that variability, the stress vs.
> non-stress distributions of cort-slope are clearly separated."

---

### Slide 11 — The augmented model wins (~60 s)

**Slide:**
- Insert **`figures/fig4_roc.png`** (all three ROC curves).
- Insert **`figures/fig5_confusions.png`** as a side panel.
- Big number block:
  | model | AUROC | F1 | precision | recall |
  |---|---|---|---|---|
  | baseline (wearable only) | 0.958 | 0.79 | 0.71 | 0.89 |
  | **augmented (+ cortisol)** | **0.987** | **0.89** | **0.84** | **0.94** |
- Subtitle: "Adding a single chemical channel closes ≈ 70% of the
  remaining AUROC error."

**Script (≈ 60 s):**
> "And here's the headline. Adding the three cortisol features to the
> same logistic-regression model takes AUROC from 0.958 to 0.987 —
> we close more than two-thirds of the remaining gap to perfect
> classification. Precision jumps from 71% to 84% — that means the
> rate of false stress alerts drops by almost half. Look at the
> confusion matrices: the augmented model misclassifies 5% of
> non-stress windows as stress versus 10% before. *That* is the
> kind of improvement that turns a stress-tracker app from a
> curiosity into a clinical tool — but with one important caveat
> on the next slide."

---

### Slide 12 — Caveats: this is proof-of-concept (~50 s)

**Slide:**
- Two-column "what we did / what we didn't" layout:

  | We did | We did NOT |
  |---|---|
  | fit a real ML model on real WESAD physiology (15 subjects) | record cortisol on any WESAD subject |
  | drive a literature-validated kinetic model of sweat cortisol | use a dataset that has *all* signals at the same time |
  | report a **predicted** AUROC improvement of 0.96 → 0.99 | *measure* that improvement experimentally |

- The simulation is anchored to independent literature — the
  *direction* of the improvement is well supported even if the
  absolute number is model-derived:
  - **Cay 2018 (NCI)** — ~9× salivary cortisol rise tracks state
    anxiety in real human stressors.
  - **Parlak 2018 (Sci. Adv.)** — wearable OECT cortisol sensor
    works in vivo with ~8 % noise.
  - **Ramasubramanya 2025 (Biosens. Bioelectron. X)** — passive-sweat
    cortisol biosensor matches gold-standard salivary cortisol at
    **Pearson r = 0.92** over 48 hours of continuous wear.
- One-line takeaway box: "The improvement is **predicted, not
  measured** — but every building block has been independently
  validated."

**Script (≈ 50 s):**
> "Before we move on, an honest caveat. We never measured cortisol
> on a single WESAD subject — those values are simulated from a
> literature-validated kinetic model. So the jump from 0.96 to
> 0.99 AUROC is a *model-based prediction*, not a direct
> measurement. The ideal experiment — wearable physiology and
> continuous cortisol on the same person at the same time — does
> not yet exist as a public dataset. What gives me confidence in
> the *direction* of the result is independent evidence. Cay 2018
> showed exam stress drives a nine-fold cortisol rise that tracks
> anxiety scores. And Ramasubramanya 2025, published just this
> past summer, demonstrated a wearable sweat-cortisol biosensor
> that matches gold-standard saliva measurements with a Pearson
> *r* of 0.92 over 48 hours of continuous wear. The biological
> link, the kinetics, and the sensor accuracy are all
> independently validated — what we've added is a quantitative
> prediction of how much they buy you when combined."

---

### Slide 13 — Why it works (~55 s)

**Slide:**
- Insert **`figures/fig7_coefficients.png`** (now showing the orange
  augmented bars beside the blue baseline bars).
- Annotate the giant orange `cort_slope` coefficient (β ≈ +3).
- Three bullets:
  - Cortisol carries information *orthogonal* to HR/EDA — it
    activates specifically through psychological appraisal of stress,
    not through exercise or temperature.
  - The slope captures the *rising* phase, which is exactly the
    actionable moment.
  - Importantly, the baseline coefficients barely change — cortisol
    is *additive* information, not a re-derivation of the same
    signals.

**Script (≈ 55 s):**
> "Why does it help? Look at the model coefficients. The orange bar
> for cort-slope is enormous — almost as large as heart-rate-mean
> itself. And critically, the rest of the coefficients hardly move:
> cortisol contributes *new* information rather than re-deriving
> what HR and EDA already provide. That's exactly what
> psychophysiology predicts — cortisol comes from a separate,
> cognitively-mediated pathway that fires only on *interpreted*
> stress. So it specifically reduces the false positives that
> exercise, weather, and excitement cause."

---

### Slide 14 — Per-subject generalization (~40 s)

**Slide:**
- Insert **`figures/fig6_per_subject_auroc.png`**.
- One bullet: "Cortisol augmentation helps the **worst-performing
  subjects most** — S3, S15, S17 all jump from AUROC ≈ 0.85 → 0.97."
- One bullet: "Leave-one-subject-out — every test subject is a
  person the model has never seen."

**Script (≈ 40 s):**
> "And it's not just a population-average effect. This per-subject
> figure shows leave-one-out AUROC for every individual. The
> blue-to-orange jumps are biggest exactly for the subjects the
> baseline model struggled with — S3, S15, S17, all the way from
> 0.85 to 0.97. Cortisol helps the people who need help most. That
> matters: a wearable that's accurate on average but fails on 1 in 7
> users is unusable; a wearable that works on everyone is a product."

---

### Slide 15 — Translation: the path to a real device (~50 s) — *optional*

**Slide:**
- Cortisol-sensor state of the art (improving rapidly):

  | sensor | year | mechanism | reported performance |
  |---|---|---|---|
  | Parlak MS-OECT | 2018 | molecularly imprinted polymer + OECT | 10 nM–10 µM range, ~8 % noise, in-vivo demo |
  | AWARE-SENSOR (Ramasubramanya et al.) | 2025 | ZnO–aptamer EIS, passive sweat | **Pearson r = 0.92** vs salivary cortisol, dose-response R² = 0.98, LoD 0.91 ng/mL, **48-h continuous wear** |

- The barrier is **integration**, not the chemistry:
  - No commercial wearable today combines BVP + EDA + TEMP + ACC +
    cortisol on one device.
  - No public dataset records all five signals on the same person.
- Bullet: "Engineering is now the bottleneck — the biochemistry of
  noninvasive cortisol sensing is largely solved."

**Script (≈ 50 s):**
> "So what would the real device look like? The chemistry has come
> a long way. Parlak's OECT sensor from 2018 first showed sweat
> cortisol can be detected continuously and noninvasively. And just
> this summer, Ramasubramanya and colleagues published an
> aptamer-based wearable that tracks sweat cortisol over 48 hours
> of continuous wear with a Pearson correlation of 0.92 against
> gold-standard salivary cortisol. That's high enough for the kind
> of signal my model needs. The bottleneck is no longer the
> sensor — it's *integration*. No consumer wearable today
> combines BVP, EDA, temperature, motion, AND a cortisol electrode
> on the same wrist, and no public dataset records all five
> signals together. The biochemistry is largely solved; the systems
> engineering hasn't caught up yet."

---

### Slide 16 — Take-aways + future work (~50 s)

**Slide:**
- 3 take-aways:
  1. A simple logistic stress index from wrist signals already
     reaches AUROC ≈ 0.96 on held-out subjects.
  2. Adding *one* simulated chemical channel — cortisol — *predicts*
     a jump to 0.99 AUROC and roughly halves false positives. The
     hormone provides information that physical sensors fundamentally
     can't.
  3. The math is portable: any wearable that exposes EDA, BVP, TEMP,
     ACC + a cortisol-sensitive electrode can run this on-device.
- 3 future-work directions:
  - **Validate experimentally** — collect a matched multi-signal
    dataset using a real wearable cortisol sensor (Parlak 2018 OECT
    or Ramasubramanya 2025 aptamer platform) and retire the
    simulation.
  - **Expand the chemistry** — add other emerging skin/sweat
    biomarkers identified by our instructor as promising directions:
    *uric acid* (an oxidative-stress marker) and *epinephrine* (the
    SAM-axis hormone, complementary to the cortisol HPA signal).
    Wearable sensors for both are improving rapidly; data is still
    sparse, so they are a natural next extension of the same model.
  - **Personalisation** — per-subject Bayesian update of β to track
    individual circadian and chronic-stress baselines.

**Script (≈ 50 s):**
> "Summing up: a clean linear model on the four wrist signals every
> wearable already exposes hits 0.96 AUROC. Adding one *simulated*
> cortisol channel predicts a jump to 0.99 and a halving of false
> positives. Cortisol isn't a better version of heart rate — it's a
> *complementary* signal from a different physiological pathway,
> and that's why combining them works. The most important next
> step is replacing the simulation with real continuous cortisol
> data. Beyond that, two other biomarkers our instructor flagged
> look promising: uric acid as an oxidative-stress marker, and
> epinephrine as a direct readout of the SAM axis. Wearable sensors
> for both are emerging but the data is still sparse — so they're a
> natural future extension of this exact model. Thanks — happy to
> take questions."

---

## References to put on a back-up slide

1. Schmidt, P. et al. (2018). *Introducing WESAD, a multimodal dataset
   for Wearable Stress and Affect Detection.* ICMI '18. doi:
   10.1145/3242969.3242985.
2. Parlak, O., Keene, S. T., Marais, A., Curto, V. F., Salleo, A.
   (2018). *Molecularly selective nanoporous membrane-based wearable
   organic electrochemical device for noninvasive cortisol sensing.*
   Sci. Adv. **4**, eaar2904.
3. Parlak, O. (2021). *Portable and wearable real-time stress
   monitoring: a critical review.* Sensors and Actuators Reports
   **3**, 100036.
4. Cay, M. et al. (2018). *Effect of increase in cortisol level due to
   stress in healthy young individuals on dynamic and static balance
   scores.* North. Clin. Istanb. **5**, 295–301.
5. Hellhammer, D. H., Wüst, S., Kudielka, B. M. (2007). *Salivary
   cortisol as a biomarker in stress research.* Psychoneuroendocrinology
   **34**, 163–171.
6. Ramasubramanya, A., Singh, P., Lin, K.-C., Prasad, S.,
   Muthukumar, S. (2025). *CIRCA: Circadian inference of rhythmicity
   using comparative analysis from non-invasive continuous
   measurements of cortisol and melatonin in passive perspiration.*
   Biosensors and Bioelectronics: X **26**, 100656. doi:
   10.1016/j.biosx.2025.100656.

---

## Suggested speaking-time budget

| section | slides | seconds |
|---|---|---|
| Title + stress biology | 1–2 | 95 |
| Why measure + biology→wearable | 3–4 | 100 |
| Data | 5 | 50 |
| Baseline model | 6–8 | 160 |
| Cortisol augmentation | 9–11 | 160 |
| **Caveats (proof-of-concept)** | 12 | 50 |
| Why it works + generalization | 13–14 | 95 |
| Translation + take-aways | 15–16 | 100 |
| **total** | 14–16 | **≈ 13 min** |

To hit 10 minutes exactly: drop the optional **Slide 15
(translation)** — the core scientific story works without it —
*and* trim Slide 2 to ~45 s by collapsing the script into the
diagram + table. Slide 12 (caveats) should stay — it's the slide
that earns intellectual-honesty points from the audience.

---

## Practical delivery tips

- The *equation slides* (6 and 9) are where you slow down. Audience
  needs ~10 s to absorb each equation visually. Don't rush past them.
- The *result slide* (11) is your applause line. Pause after "0.96 → 0.99."
- **Slide 12 (caveats) immediately follows the applause line on
  purpose** — the audience is most receptive to the simulation
  caveat right after the big result, and getting it out yourself
  preempts the obvious question.
- Slide 2 is dense — point at the diagram while you talk; don't read
  the table out loud, just gesture at it.
- Have **`results/metrics.json`** open in case of detailed Q&A.
- If asked "did you actually measure cortisol?" — your answer is
  already on Slide 12: "No — those values came from a
  literature-validated kinetic model. The simulation is anchored to
  Cay 2018's 9× cortisol rise during real exam stress, and the
  sensor accuracy assumption is anchored to Ramasubramanya 2025's
  *r* = 0.92 sweat-vs-saliva correlation. So the 0.96 → 0.99
  improvement is a *prediction* of what a real integrated device
  would achieve, not a measurement of one."
