# /stan define

Starte oder setze die DEFINE Phase fort.

## Anweisungen

1. Prüfe ob `stan.md` existiert
   - Falls nein: Hinweis auf `/stan init`
   - Falls ja: Weiter

2. Prüfe aktuelle Phase in `stan.md`
   - Falls bereits DEFINE: Fortsetzen
   - Falls PLAN oder CREATE: **Widerworte geben!**
     ```
     Aktuell in Phase: {phase}

     Zurück zu DEFINE bedeutet:
     - Fundamentale Änderung am Scope
     - Bisherige Planung/Arbeit eventuell obsolet

     Bist du sicher? (ja/nein)
     ```

3. Falls in DEFINE Phase:
   - Prüfe ob PRD existiert (`docs/prd.md`)
   - Falls nein: PRD interaktiv erstellen mit Template
   - Falls ja: PRD-Status prüfen und ggf. weiterarbeiten

4. PRD-Workflow:
   - Erkenne Reife des User-Inputs:
     - Vage Idee → Interview-Modus (Fragen stellen)
     - Klares Konzept → PRD strukturieren
     - Fertiges PRD → Validieren gegen Criteria

5. Nach PRD-Erstellung:
   - Führe Criteria-Checks durch (`prd.md` hat criteria in frontmatter)
   - Zeige Ergebnis der Checks
   - Bei alle required=true erfüllt: PRD auf `status: approved` setzen

6. Bei approved PRD:
   ```
   PRD approved!

   Nächster Schritt: /stan plan
   ```

## Wichtig

- DEFINE ist interaktiv, nicht autonom
- User-Input ist König - strukturieren, nicht erfinden
- Bei Unklarheit: FRAGEN, nicht annehmen
