# Golden Examples: Schlechte Evidenz

## Example 1: Keine echte Evidenz
> "User wollen das bestimmt. Andere Apps haben das auch."

**Expected Score: 1**
- sources-present: 1 - Keine echte Quelle
- sources-cited: 1 - Keine Details
- not-assumed: 1 - "Bestimmt" ist Annahme
- relevant-to-hypothesis: 1 - Keine Verbindung
- contradictions-addressed: 1 - Keine
- recency: 1 - Undatiert

---

## Example 2: Vage Verweise
> "Studien zeigen, dass User CSV-Import bevorzugen. Experten sind sich einig, dass dies Best Practice ist."

**Expected Score: 2**
- sources-present: 2 - "Studien" angedeutet
- sources-cited: 1 - Welche Studien? Welche Experten?
- not-assumed: 2 - Behauptung ohne Beleg
- relevant-to-hypothesis: 3 - Thematisch passend
- contradictions-addressed: 1 - Keine
- recency: 1 - Undatiert

---

## Example 3: Nur Bauchgefühl
> "Ich glaube, unsere User würden davon profitieren. Das macht einfach Sinn."

**Expected Score: 1**
- sources-present: 1 - Keine Quellen
- sources-cited: 1 - Nichts zu zitieren
- not-assumed: 1 - Explizit "ich glaube"
- relevant-to-hypothesis: 2 - Vage Verbindung
- contradictions-addressed: 1 - Keine
- recency: 1 - N/A

---

## Example 4: Veraltete Daten
> **Marktanalyse (2018):** Damals hatten 60% der Konkurrenten CSV-Import.
> **User Feedback:** "Vor ein paar Jahren hat mal jemand danach gefragt."

**Expected Score: 2**
- sources-present: 3 - Quellen vorhanden
- sources-cited: 2 - Jahr genannt, aber veraltet
- not-assumed: 3 - Daten existieren, aber alt
- relevant-to-hypothesis: 3 - Thematisch relevant
- contradictions-addressed: 1 - Keine
- recency: 1 - 2018 ist zu alt

---

## Example 5: Irrelevante Evidenz
> **User Research:** 15 Interviews über Farbpräferenzen für das Dashboard. 80% bevorzugen Blau.
> **Interne Daten:** Die Homepage hat 50.000 Besucher/Monat.

**Expected Score: 2**
- sources-present: 4 - Quellen vorhanden
- sources-cited: 4 - Details genannt
- not-assumed: 4 - Echte Daten
- relevant-to-hypothesis: 1 - Keine Verbindung zu Import
- contradictions-addressed: 1 - Keine
- recency: 3 - Undatiert
