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

5. Zeige Ergebnis:
   ```
   STAN Health Check
   =================

   Struktur: ✓ OK / ✗ Problem
   Dokumente: ✓ OK / ✗ Problem
   Templates: ✓ OK / ✗ Problem
   Reviews: ✓ OK / ✗ {count} offen

   Details:
   {problems}

   Empfehlungen:
   {recommendations}
   ```

## Wichtig

- Healthcheck ist rein informativ, ändert nichts
- Zeige konkrete Lösungsvorschläge für Probleme
