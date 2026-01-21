# /stan healthcheck

Prüfe Konsistenz des STAN-Projekts.

## Anweisungen

1. Prüfe Projekt-Struktur:
   - [ ] `stan.md` existiert
   - [ ] `docs/` Verzeichnis existiert
   - [ ] Templates verfügbar

2. Prüfe Dokument-Konsistenz:
   - [ ] PRD hat gültiges Frontmatter
   - [ ] PRD Criteria sind auflösbar
   - [ ] Plan hat gültiges Frontmatter
   - [ ] Plan Criteria sind auflösbar

3. Prüfe Template-Criteria Verknüpfung:
   - Für jedes Template:
     - Lies Frontmatter
     - Prüfe ob alle Criteria in `criteria:` Liste existieren
     - Melde fehlende Criteria

4. Prüfe offene Reviews:
   - Pending Learnings?
   - Tasks ohne Akzeptanzkriterien?
   - PRD ohne Status?

5. **Criteria-Evaluation** (wenn `--eval` Flag):
   - Für jedes Dokument mit Criteria im Frontmatter:
     - Lies den passenden Evaluator aus `tests/criteria-eval/evaluators/{criteria}.md`
     - Folge den Anweisungen im Evaluator
     - Gib das JSON-Ergebnis aus
   - Beispiel: PRD hat `criteria: [goal-quality]`
     → Lies `tests/criteria-eval/evaluators/goal-quality.md`
     → Evaluiere das Ziel aus dem PRD gegen die SMART-Kriterien
     → Zeige Score und Verbesserungsvorschläge

6. Zeige Ergebnis:
   ```
   STAN Health Check
   =================

   Struktur: ✓ OK / ✗ Problem
   Dokumente: ✓ OK / ✗ Problem
   Templates: ✓ OK / ✗ Problem
   Reviews: ✓ OK / ✗ {count} offen

   [wenn --eval]
   Criteria Evaluation:
   - goal-quality: 4.2/5 ✓ PASSED
     - concrete: 5/5
     - measurable: 4/5 - "Zeitrahmen könnte präziser sein"
     - ...

   Details:
   {problems}

   Empfehlungen:
   {recommendations}
   ```

## Wichtig

- Healthcheck ist rein informativ, ändert nichts
- Zeige konkrete Lösungsvorschläge für Probleme
