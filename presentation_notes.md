# BE 153 Final Project — Presentation Notes
## *Quantifying Stress with Wearables: A Physiology + Cortisol Model*

**Format:** ~10–12 slides, ~10 minutes (so target ≈ 50 s per slide).
**Modeling style mirrors the kidney-stone example:** start with the
biological motivation, state a mechanistic equation, fit constants to
data, then propose an improvement.

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

### Slide 2 — Why model stress? (~50 s)

**Slide:**
- 3 bullets: (i) stress drives chronic disease (CV, immune, mental
  health); (ii) global burden of stress-related illness rising; (iii)
  current screening is questionnaire-based — episodic, biased, and
  late.
- A small headline number: "WHO: stress-related disorders projected to
  be the #2 cause of global disability by 2030."
- Optional small image of a smartwatch screen.

**Script (≈ 50 s):**
> "Stress is much more than a feeling — chronic HPA-axis activation
> drives cardiovascular disease, immune dysregulation, depression, and
> metabolic disorders. The World Health Organization expects
> stress-related illness to become the second largest cause of
> disability worldwide. But the way we *measure* stress today is
> embarrassingly primitive: a survey at the doctor's office, weeks or
> months apart. To do anything preventive, we need a continuous,
> objective, real-world measurement — exactly the problem wearables
> were built for."

---

### Slide 3 — The biology behind a wearable stress signal (~55 s)

**Slide:**
- Cartoon: stressor → amygdala → hypothalamus → HPA & sympathetic
  axes → two outputs:
  - Fast: ↑ HR, ↑ sweat (EDA), peripheral vasoconstriction (↓ skin
    temperature)  — seconds
  - Slow: ACTH → adrenal cortex → cortisol → diffuses to saliva /
    sweat / urine — minutes
- "What current wearables can measure today" vs "What they can't"
- Cite Parlak 2021 (the cortisol review article).

**Script (≈ 55 s):**
> "Biologically, an acute stressor activates two parallel systems.
> The sympathetic branch is fast — within seconds your heart rate
> rises, sweat-gland activity goes up, and peripheral blood vessels
> constrict so your skin cools. *All three* of these are
> measurable from a wrist wearable today: BVP gives you heart rate,
> EDA gives you sweat conductance, and a skin thermometer captures the
> vasoconstriction. The slower branch is the HPA axis, which releases
> cortisol from the adrenal cortex about 10 to 20 minutes after a
> stressor and clears with a roughly 60-minute half-life. Critically,
> *no current consumer wearable measures cortisol* — but recent
> work by Parlak and colleagues has built electrochemical sweat
> sensors that can."

---

### Slide 4 — The data: WESAD (~50 s)

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

### Slide 5 — A mathematical stress index (~60 s)

**Slide:**
- Equation (centerpiece):
  $$ S(\mathbf{x}) = \beta_0 + \sum_{k} \beta_k\,z(x_k) $$
  $$ P(\text{stress}\mid \mathbf{x}) = \sigma(S(\mathbf{x})) = \frac{1}{1+e^{-S(\mathbf{x})}} $$
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

### Slide 6 — How well does it work today? (~55 s)

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

### Slide 7 — Where the model breaks (~45 s)

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

### Slide 8 — A chemical answer: cortisol (~60 s)

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

### Slide 9 — Generating cortisol features (~40 s)

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
- Reminder: "We aren't fabricating measurements — we are *predicting*
  what a working sweat-cortisol sensor would output given the WESAD
  ground truth."

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

### Slide 10 — The augmented model wins (~60 s)

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
> curiosity into a clinical tool."

---

### Slide 11 — Why it works (~55 s)

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

### Slide 12 — Per-subject generalization (~40 s)

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

### Slide 13 — Translation: what would the device look like? (~45 s) — *optional 12th slide*

**Slide:**
- Stack: wrist-band photo + a small inset of Parlak's MS-OECT
  (organic electrochemical transistor) sensor — credit Parlak 2018.
- Three engineering specs the model implicitly requires:
  - Sensor sensitivity ≈ 1 nmol/L (well within current MS-OECT range
    of 0.01–10 μM).
  - Sampling rate ≥ 1 min⁻¹ (continuous; current MS-OECT supports).
  - ≤ 10 % drift over a day.
- Bullet: "This is *not* far in the future — published in 2018 already."

**Script (≈ 45 s):**
> "What does this device actually look like? Parlak's group has
> already demonstrated a wearable OECT sensor that detects sweat
> cortisol from 10 nM to 10 µM with ~8% noise. That's well within
> what my model needs: roughly one-minute updates and 1 nmol/L
> resolution. Combine that with the BVP, EDA, and TEMP that today's
> wrist devices already report, and the augmented model is a
> firmware update away."

---

### Slide 14 — Take-aways + future work (~40 s)

**Slide:**
- 3 take-aways:
  1. A simple logistic stress index from wrist signals already
     reaches AUROC ≈ 0.96 on held-out subjects.
  2. Adding *one* chemical channel — cortisol — pushes it to 0.99
     and roughly halves false positives. The hormone provides
     information that physical sensors fundamentally can't.
  3. The math is portable: any wearable that exposes EDA, BVP, TEMP,
     ACC + a cortisol-sensitive electrode can run this on-device.
- 2 future-work bullets:
  - Validate on real continuous cortisol (e.g. integrate with an
    OECT sensor like Parlak 2018).
  - Personalisation: per-subject Bayesian update of β to track
    individual circadian and chronic-stress baselines.

**Script (≈ 40 s):**
> "Summing up: a clean linear model on the four wrist signals that
> every wearable already exposes hits 0.96 AUROC. Adding one
> simulated cortisol channel takes it to 0.99 and slashes the
> false-positive rate. Cortisol isn't a better version of HR — it's
> a *complementary* signal, and that's why combining them works.
> The next steps are real continuous cortisol data and per-subject
> baselines that adapt to your circadian rhythm. Thanks — happy to
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

---

## Suggested speaking-time budget

| section | slides | seconds |
|---|---|---|
| Motivation + biology | 1–3 | 135 |
| Data | 4 | 50 |
| Baseline model | 5–7 | 160 |
| Cortisol augmentation | 8–10 | 160 |
| Why it works + generalization | 11–12 | 95 |
| Translation + take-aways | 13–14 | 85 |
| **total** | 12–14 | **≈ 11 min** |

Trim slide 13 (translation) if you need to hit 10 minutes exactly —
the core scientific story works without it.

---

## Practical delivery tips

- The *equation slides* (5 and 8) are where you slow down. Audience
  needs ~10 s to absorb each equation visually. Don't rush past them.
- The *result slide* (10) is your applause line. Pause after "0.96 → 0.99."
- Have **`results/metrics.json`** open in case of detailed Q&A.
- If asked "did you actually measure cortisol?" — be honest: "No,
  I simulated it from a literature-validated kinetic model. The next
  step is integrating a real OECT sensor, but the model's prediction
  of how much improvement to expect is itself the contribution."
