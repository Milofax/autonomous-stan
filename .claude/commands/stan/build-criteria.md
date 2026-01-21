# /stan build-criteria

Baue ein neues Criteria interaktiv.

## Anweisungen

1. Sammle Criteria-Informationen:
   - **Name:** Wie soll das Criteria heißen? (z.B. "a11y-checks", "security-review")
   - **Kategorie:** code, text, strategy, oder neue Kategorie
   - **Beschreibung:** Was prüft dieses Criteria?

2. Baue Checks interaktiv:
   - Für jeden Check fragen:
     - **ID:** Kurzer Identifier (z.B. "contrast-ratio")
     - **Frage:** Was wird geprüft? (als Frage formuliert)
     - **Required:** Muss erfüllt sein? (ja/nein)
     - **Auto:** Automatisch prüfbar? (ja/nein)
     - Falls Auto=ja: Welcher Command?

3. Wiederhole bis User sagt "fertig"

4. Am ENDE: Templates identifizieren
   - Liste existierende Templates
   - Frage: Welche Templates könnten von diesem Criteria profitieren?
   - Bei Auswahl: Anbieten die Templates zu aktualisieren

5. Erstelle Criteria-Datei:
   ```yaml
   name: {Name}
   description: {Beschreibung}

   checks:
     - id: {id}
       question: "{Frage}"
       required: {true/false}
       auto: {true/false}
       command: "{command}"  # nur wenn auto=true
   ```

6. Speichere in `criteria/{kategorie}/{name}.yaml`

7. Falls Templates aktualisiert:
   - Füge Criteria zu Template-Frontmatter hinzu
   - Zeige welche Templates aktualisiert wurden

8. Bestätige:
   ```
   Criteria erstellt: criteria/{kategorie}/{name}.yaml

   Checks: {count}
   Auto-Checks: {auto_count}

   Verknüpfte Templates:
   - {template_1}
   - {template_2}
   ```

## Wichtig

- 1 YAML = 1 Criteria (atomar)
- Fragen sollten mit Ja/Nein beantwortbar sein
- Auto-Commands müssen exit 0 bei Erfolg liefern
