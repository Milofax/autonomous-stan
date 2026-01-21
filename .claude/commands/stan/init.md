# /stan init

Initialisiere ein STAN-Projekt im aktuellen Verzeichnis.

## Anweisungen

1. Prüfe ob bereits eine `stan.md` existiert
   - Falls ja: Frage ob überschrieben werden soll
   - Falls nein: Weiter

2. Sammle Projekt-Informationen interaktiv:
   - **Projekt-Name:** Wie heißt das Projekt?
   - **Beschreibung:** Kurze Beschreibung in 1-2 Sätzen
   - **Ziel:** Was soll erreicht werden?

3. Erstelle `stan.md` basierend auf Template:
   - Nutze Template aus `templates/stan.md.template`
   - Ersetze Platzhalter mit gesammelten Infos
   - Setze Phase auf `DEFINE`

4. Erstelle `docs/` Verzeichnis falls nicht vorhanden

5. Bestätige Initialisierung:
   ```
   STAN initialisiert!

   Projekt: {name}
   Phase: DEFINE

   Nächster Schritt: /stan define
   ```

## Wichtig

- NIEMALS eine existierende stan.md ohne Bestätigung überschreiben
- Das Datum im Template durch aktuelles Datum ersetzen
- Nach Init ist die Phase immer DEFINE
