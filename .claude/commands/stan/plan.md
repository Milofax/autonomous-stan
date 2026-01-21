# /stan plan

Starte oder setze die PLAN Phase fort.

## Anweisungen

1. Prüfe Vorbedingungen:
   - `stan.md` existiert?
   - PRD `status: approved`?
   - Falls nein: Hinweis und STOP

2. Prüfe aktuelle Phase:
   - Falls DEFINE: Wechsel zu PLAN (normal)
   - Falls PLAN: Fortsetzen
   - Falls CREATE: **Widerworte geben!**
     ```
     Aktuell in CREATE Phase!

     Zurück zu PLAN bedeutet:
     - Implementierung pausieren
     - Eventuell neue Tasks definieren

     Grund für Rückschritt?
     ```

3. Falls in PLAN Phase:
   - Prüfe ob Plan existiert (`docs/plan.md`)
   - Falls nein: Plan aus PRD ableiten
   - Falls ja: Plan-Status prüfen

4. Plan-Erstellung:
   - Lies PRD und identifiziere Tasks
   - Erstelle Tasks mit:
     - ID (T-001, T-002, ...)
     - Beschreibung
     - Dependencies
     - Betroffene Dateien
     - Akzeptanzkriterien
   - Erstelle Dependency Graph
   - Identifiziere parallelisierbare Tasks

5. Nach Plan-Erstellung:
   - Führe Criteria-Checks durch
   - Bei alle required=true erfüllt: Mindestens 1 Task auf `status: ready`

6. Bei ready Tasks:
   ```
   Plan ready!

   Tasks: {count}
   Parallelisierbar: {parallel_count}

   Nächster Schritt: /stan create
   ```

## Wichtig

- Tasks sollten konkret und umsetzbar sein
- Dependencies MÜSSEN vollständig sein
- Parallelisierung nur wo SICHER möglich
