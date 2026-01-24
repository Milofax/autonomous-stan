# Golden Examples: Schlechte Success Metrics

## Example 1: Komplett vage
> "Wir wollen mehr User und bessere Zahlen."

**Expected Score: 1**
- metrics-defined: 1 - Keine konkreten Metrics
- baseline-present: 1 - Keine Baseline
- target-specific: 1 - "Mehr" und "besser" sind vage
- measurement-method: 1 - Nicht dokumentiert
- north-star: 1 - Keine Priorisierung
- no-vanity-metrics: 1 - "Mehr User" ist Vanity
- leading-lagging: 1 - Nicht unterschieden

---

## Example 2: Keine Baselines
> | Metrik | Ziel |
> |--------|------|
> | Conversion Rate | Erhöhen |
> | User Satisfaction | Verbessern |
> | Page Load Time | Schneller |

**Expected Score: 2**
- metrics-defined: 3 - Metrics genannt
- baseline-present: 1 - Keine Baselines
- target-specific: 1 - "Erhöhen", "Verbessern", "Schneller" sind vage
- measurement-method: 1 - Nicht dokumentiert
- north-star: 1 - Keine Priorisierung
- no-vanity-metrics: 3 - Mix
- leading-lagging: 1 - Nicht unterschieden

---

## Example 3: Nur Vanity Metrics
> | Metrik | Baseline | Ziel |
> |--------|----------|------|
> | Pageviews | 100k/Monat | 200k/Monat |
> | App Downloads | 5.000 | 10.000 |
> | Social Media Followers | 2.000 | 5.000 |
>
> **North Star Metric:** Pageviews

**Expected Score: 2**
- metrics-defined: 4 - Quantitative Metrics
- baseline-present: 4 - Baselines vorhanden
- target-specific: 4 - Konkrete Zahlen
- measurement-method: 1 - Nicht dokumentiert
- north-star: 3 - Definiert aber Vanity
- no-vanity-metrics: 1 - Alles Vanity Metrics
- leading-lagging: 1 - Nicht unterschieden

---

## Example 4: Keine Messmethode
> | Metrik | Baseline | Ziel |
> |--------|----------|------|
> | User Happiness | Niedrig | Hoch |
> | Code Quality | Mittel | Gut |

**Expected Score: 2**
- metrics-defined: 2 - Nicht wirklich quantitativ
- baseline-present: 2 - "Niedrig", "Mittel" sind keine echten Baselines
- target-specific: 2 - "Hoch", "Gut" sind subjektiv
- measurement-method: 1 - Wie misst man "Happiness"?
- north-star: 1 - Keine Priorisierung
- no-vanity-metrics: 2 - Unklar ob actionable
- leading-lagging: 1 - Nicht unterschieden
