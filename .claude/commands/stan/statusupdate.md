# /stan statusupdate

Zeige aktuellen STAN-Status und erlaube manuelle Änderungen.

## Anweisungen

1. Prüfe ob `stan.md` existiert
   - Falls nein: Hinweis auf `/stan init`

2. Zeige aktuellen Status:
   ```
   STAN Status
   ===========

   Projekt: {name}
   Phase: {phase}
   Current Task: {task}
   Last Updated: {date}

   Dokumente:
   - PRD: {prd_status}
   - Plan: {plan_status}

   Learnings:
   - Hot: {hot_count}
   - Recent: {recent_count}
   - Pending: {pending_count}

   Session:
   - Test History: {test_count} runs
   - Last Test: {last_test_status}
   ```

3. Frage nach gewünschter Aktion:
   - `[1]` Phase manuell ändern
   - `[2]` Current Task setzen
   - `[3]` Pending Learnings anzeigen
   - `[4]` Nichts ändern

4. Bei Phase-Änderung:
   - Zeige Widerworte wenn signifikant (z.B. CREATE → DEFINE)
   - Bestätigung erforderlich
   - Update stan.md

5. Bei Task-Änderung:
   - Liste verfügbare Tasks aus plan.md
   - Update Current Task in stan.md

## Wichtig

- Status ist informativ UND interaktiv
- Phase-Änderungen haben Konsequenzen - transparent kommunizieren
