# /stan create

Starte die CREATE Phase (autonome Ausführung).

## Anweisungen

1. Prüfe Vorbedingungen:
   - `stan.md` existiert?
   - Mindestens 1 Task `status: ready`?
   - Falls nein: Hinweis und STOP

2. Prüfe aktuelle Phase:
   - Falls PLAN: Wechsel zu CREATE (normal)
   - Falls CREATE: Fortsetzen mit nächstem Task
   - Falls DEFINE: **BLOCKIERT**
     ```
     Noch in DEFINE!

     CREATE erfordert:
     1. Approved PRD
     2. Mindestens 1 ready Task

     Nutze erst /stan define und /stan plan
     ```

3. CREATE ist AUTONOM:
   - Arbeite Tasks der Reihe nach ab
   - Beachte Dependencies
   - Führe Tests nach jeder Änderung aus
   - Committe nach jedem fertigen Task

4. Pro Task:
   - Setze Task auf `status: in_progress` in stan.md
   - Implementiere gemäß Akzeptanzkriterien
   - Führe relevante Tests aus
   - Bei GRÜN: Task auf `status: done`
   - Commit mit Referenz zum Task

5. Bei Problemen:
   - 3-Strikes Regel beachten
   - Bei fundamentalen Problemen: Reconciliation zu DEFINE
   - Pending Learnings vor Commit speichern

6. Nach allen Tasks:
   ```
   CREATE Phase abgeschlossen!

   Erledigte Tasks: {done_count}
   Commits: {commit_count}
   Learnings: {learning_count}

   Empfehlung: Review der Learnings mit /stan learnings
   ```

## Wichtig

- CREATE ist AUTONOM - wenig User-Interaktion
- Tests MÜSSEN grün sein vor Commit
- Learnings MÜSSEN gespeichert sein vor Commit
- Bei 3-Strikes: STOPP und Reflexion
