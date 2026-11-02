# Codex-Arbeitsauftrag: Matching über sechs Wochen verbessern

Repository: https://github.com/kalkprofijanek/kalkpilot-by-janek

Ziel: KalkPilot soll fachlich ungeeignete Referenzen seltener vorschlagen, passende Referenzen zuverlässiger finden und unbekannte Anforderungen nachvollziehbar offenlassen. Die statische Browser-App und der bewusste Excel-/JSON-Austausch mit KI bleiben erhalten. Keine automatische Preisfreigabe.

Die Wochen sind sechs aufeinanderfolgende Arbeitspakete. Codex führt sie nicht automatisch nach Kalender aus. Pro Paket eine neue Aufgabe starten, Ergebnisse prüfen und den zugehörigen Pull Request abschließen. Ein noch offenes Prüfkriterium wird als offen dokumentiert, nicht durch Zeitablauf als erfüllt behandelt.

## Ausgangslage und erster GitHub-Schritt

Dieser Auftrag entstand aus dem lokalen Arbeitsstand auf Branch `work`: Fachprüfung, Kandidatensuche, Sammelübernahme, Werkzeuge und synthetische Regressionen. Vor dem Start prüfen, ob dieser Stand bereits über einen Basis-PR gesichert wurde. Andernfalls zuerst einen eigenen Basis-PR erstellen. Bestehende Änderungen nicht zurücksetzen, überschreiben oder nochmals unabhängig nachbauen.

Zum bisherigen Stand gehören:

- Zwei öffentliche Original-LVs: Ulm mit 244 und Heidelberg mit 585 Positionen.
- 829 Importpositionen mit Abgleich von sieben Feldern, 285.480 projektübergreifende Positionsvergleiche je Lauf.
- 60 vorbereitete Originalfälle, deren fachliche Erwartungen noch unbestätigt sind.
- 123 synthetische Fachfälle und 60 automatisierte Browser-/Cloud-Tests.
- Konkrete Korrekturen für Rohrmaße, AVV-Schreibweisen, Tätigkeitsabgrenzung, Bauteilhöhen und Bogenwinkel.

Die 123 bestandenen synthetischen Fälle sind keine Trefferquote auf Original-LVs. Die beiden bislang untersuchten Projekte sind Entwicklungsdaten und dürfen nicht später als unabhängiger Abschlusstest ausgegeben werden.

Arbeitsdateien dieser Sitzung:

- `/workspace/analysis/public-lv-review/KalkPilot-Praxispruefung.zip`
- `/workspace/analysis/public-lv-review/Pruefbericht.html`
- `/workspace/analysis/public-lv-review/import-audit.json`
- `/workspace/analysis/public-lv-manifest.json`

Diese Dateien liegen außerhalb des Repositories und sind nicht automatisch in einer neuen Codex-Sitzung verfügbar. Das ZIP separat sichern, beispielsweise im freigegebenen Firmenablageort. Vor jeder neuen Sitzung das Vorhandensein und die Prüfsummen der benötigten Daten prüfen. Ohne Originaldateien darf Codex weiter an Werkzeugen und synthetischen Tests arbeiten, aber keinen angeblich ausgeführten Originaldatenlauf melden. Neue Sitzungen brauchen den passenden freigegebenen Zugriff oder die benötigten Dateien.

Weitere Grundlagen: [öffentliche LV-Prüfung](OEFFENTLICHE_LV_PRUEFUNG.md), [Matching-Vertiefung](MATCHING_VERTIEFUNG.md), [Veröffentlichung](VEROEFFENTLICHUNG.md).

## Woche 1: Bestand aufbauen und Testdaten trennen

1. Basis-PR sichern und den eingecheckten Commit als Ausgangsstand festhalten.
2. Öffentlich erreichbare weitere LVs aus passenden Gewerken suchen. Richtgröße: sechs bis zehn LVs insgesamt; mindestens drei zusätzliche, zuvor ungenutzte Projekte für den späteren Test zurückhalten. Verfügbarkeit und zulässige Nutzung prüfen; fehlende geeignete LVs ausdrücklich dokumentieren.
3. Die vorhandene API liefert Bekanntmachungen. GAEB-Dateien werden über deren Links auf den Vergabeplattformen gesucht. Downloadwege, Nutzungsbedingungen, Datum, Projekt, Dateiversion und SHA-256 festhalten. Keine Registrierungen, Anmeldungen oder Umgehungen von Zugangsbeschränkungen durchführen.
4. Die relevanten X83/D83-Dateien gezielt abrufen; umfangreiche Pläne und Anlagen nicht unnötig herunterladen. Quellen außerhalb von Git ablegen.
5. Importkontrolle ausführen: Positionenzahl, Originalkennung, OZ, Titel, vollständige Texte, Mengen und Einheiten. Abweichungen blockieren den jeweiligen Vergleichslauf.
6. Entwicklungs- und Testprojekte vor weiteren Regeländerungen fest zuordnen. Wiederveröffentlichungen, nahezu identische LVs und Projektversionen gemeinsam behandeln, damit keine Kopien über die Trennung hinweg gelangen.

Lieferung: Quellenmanifest, Importberichte, versionierte Datenaufteilung über Dateiprüfsummen, PR mit notwendigen Werkzeugverbesserungen und einer kurzen Zusammenfassung ohne Originaltexte.

## Woche 2: Fachlich bestätigte Vergleichsfälle aufbauen

1. Die vorhandenen 60 Originalfälle prüfen und durch typische Fehlerfälle ergänzen: Rohrmaße, Bögen, Einbautiefe, Bauhöhen, Transport, Boden, Abfall, Bauzaun, Nebenleistungen und Fälle ohne passende Referenz.
2. Je Fall erfassen: Datenstand, Ziel-ID, Projekt, zulässige Referenz-IDs, Status `passend`, `teilweise`, `kein_belastbarer_treffer` oder `unklar`, Originalbelege und fachliche Begründung.
3. Preis- und Faktorfragen separat erfassen. Eine ähnliche Geräteausstattung bestätigt keine gleiche Leistung.
4. Codex und Subagents dürfen Vorbewertungen erstellen. Diese bleiben `agent_proposed`. Nur eine nachvollziehbare Prüfung durch dich oder eine benannte fachkundige Person setzt `expert_confirmed`. Unklare Fälle bleiben offen.
5. Ein `kein_belastbarer_treffer` verlangt eine Prüfung des zugehörigen Referenzbestands; die ersten drei Suchvorschläge allein reichen als Nachweis nicht.
6. Einfache Prüfoberfläche oder Excel-Arbeitsblatt mit Export der Labels bereitstellen. Referenz-IDs eines KI-Auftrags nicht mit den globalen IDs einer Rangliste verwechseln.

Lieferung: nachvollziehbarer, zunächst kleiner Experten-Prüfsatz. Zielgröße für die erste Runde sind die vorhandenen 60 Fälle; fehlende Fachbestätigungen nicht durch KI-Etiketten ersetzen.

## Woche 3: Fehler mit größter Wirkung korrigieren

1. Zuerst die bestätigten Fehlzuordnungen mit hoher Punktzahl auswerten.
2. Je Änderung den konkreten Fehler reproduzieren und mindestens ein fachlich gültiges Gegenbeispiel ergänzen. Originaltexte nicht ins öffentliche Repository übernehmen; kleine synthetische Fälle formulieren.
3. Anforderungen, Leistungsumfang und Arbeitsbedingungen vergleichen, statt Punktwerte pauschal anzuheben. Bereiche, fehlende Angaben, verschiedene Bezugsbasen und teilweise abgedeckte Leistungen getrennt behandeln.
4. Kandidatensuche im großen Bestand prüfen: Wird eine passende Referenz bereits vor der ausführlichen Bewertung abgeschnitten? Den vollständigen Vergleich und die tatsächlich begrenzte App-Suche getrennt messen.
5. Bestehende Fachdeckel, Projektausschlüsse, Einheitenfilter und Trennung von Preis und Passung erhalten.

Lieferung: kleine, einzeln prüfbare PRs nach Fehlerfamilie, jeweils mit Beispiel, Gegenbeispiel und Vorher-/Nachher-Ergebnis. Keine Sammeländerung mit vielen unzuordenbaren Regeln.

## Woche 4: KI-Austausch und fachliche Prüfung verbessern

1. Belege, fehlende Anforderungen, Teildeckung und Gegenargumente im Excel-/JSON-Auftrag verbessern.
2. Alle Referenzen des freigegebenen Bestands für den Auftrag erhalten; eine enge Regel-Vorauswahl nicht als vollständigen Bestand ausgeben.
3. Bei Größenlimits kontrollierte Pakete mit eindeutiger Kennung und geprüfter Vollständigkeit verwenden. Keine stillen Kürzungen von Texten oder Referenzen.
4. Antwortimport, geänderte Datenstände, falsche IDs, erfundene Textbelege und widersprüchliche KI-Aussagen durch dieselben Prüfungen führen.
5. Einen Vergleich mit einem externen KI-Dienst nur durchführen, wenn der entsprechende Upload/Dienst in der Sitzung ausdrücklich freigegeben wurde. Ohne einen solchen Lauf nur den Datei- und Prüfablauf als getestet melden.

Lieferung: getestete Austauschpakete und verständliche Prüfansicht. Keine Modellzugänge, API-Schlüssel oder neue Serverinfrastruktur voraussetzen.

## Woche 5: An zurückgehaltenen Projekten messen

1. Implementierung, Regeln, Prompt, Datenstand, Kandidatenlimits und Schwellen einfrieren und mit Commit/Hash dokumentieren.
2. Die zuvor zurückgehaltenen Projekte erstmals für die Auswertung verwenden. Das eigene Projekt und dessen Kopien dürfen nicht unter den Referenzen sein.
3. Nur fachlich bestätigte Fälle in Genauigkeitskennzahlen aufnehmen. Den Anteil unklarer und unbestätigter Fälle separat ausweisen. Nach Projekt und Gewerk aufschlüsseln.
4. Folgende Kennzahlen immer als Zähler und Nenner berichten:
   - Top-1: bestätigte Fälle mit zulässiger erster Referenz / bestätigte Fälle mit vorhandener passender Referenz.
   - Recall@3: bestätigte Fälle mit mindestens einer zulässigen Referenz unter den ersten drei / bestätigte Fälle mit vorhandener passender Referenz.
   - Falscher Treffer ohne Referenz: Fälle mit unzulässigem belastbaren Vorschlag / bestätigte Fälle ohne passende Referenz.
   - Gefährliche automatische Übernahmen: fachlich falsche automatisch übernommene Referenzen / geprüfte automatische Übernahmen.
   - Offene Prüfungen und Laufzeit getrennt von der Trefferqualität.
5. Strenge Passung und fachlich nutzbare Teilansätze getrennt auswerten. Mehrere zulässige Referenzen berücksichtigen.
6. Basisstand und neuen Stand auf exakt demselben Datenstand vergleichen. Eine höhere Durchschnittspunktzahl ist kein Qualitätsnachweis.
7. Nach jeder Änderung aufgrund dieses Testlaufs gelten die verwendeten Fälle als Entwicklungsdaten. Einen erneuten unabhängigen Test auf weiteren ungenutzten Projekten planen.

Lieferung: reproduzierbarer Bericht mit vollständigen Nennern, Daten-/Versionsnachweisen, Fehlerbeispielen und offenen Grenzen. Ohne Fachlabels oder ausreichende neue Projekte keinen bestandenen Expertenbenchmark behaupten.

## Woche 6: Pilot und Veröffentlichung

1. Die von dir bestätigten Pilotfälle im Firmenbrowser durchspielen: Upload, Referenzwahl, Alternativen, offene Hinweise und bewusste Übernahme.
2. Falls passende echte Kalkulationsreferenzen vorhanden und freigegeben sind, einen iTWO-Reimport separat prüfen. Öffentliche LV-Texte allein liefern keine Kalkulationsfreigabe.
3. Alle relevanten Regressionen und GitHub-Checks abschließen, Versionshinweise und bekannte Grenzen aktualisieren.
4. Release-PR erstellen. Du prüfst und mergst ihn nach `main`; nicht selbständig mergen.
5. Den tatsächlichen Deploy-Schritt von **Publish browser app** und danach die Live-App prüfen. Erfolgreicher Build, erstellter PR und veröffentlichte Website sind drei verschiedene Zustände.

Lieferung: freigabefähiger PR, Pilotbericht und klare Liste verbleibender fachlicher Fragen.

## Subagents einsetzen

Ein Hauptagent verantwortet Datenstand, Integration, Ergebnisse und den PR. Pro Arbeitspaket höchstens drei gezielt beauftragte Subagents gleichzeitig; nicht alle Rollen über sechs Wochen dauerhaft laufen lassen.

| Rolle | Konkreter Auftrag | Grenze |
| --- | --- | --- |
| Daten/Import | Quellen, Prüfsummen, Dubletten und Importverluste untersuchen; reproduzierbare Befunde liefern | Keine erfundenen Kostenansätze, keine Originaldaten in Git |
| Fachfälle/Benchmark | Schwierige Paare, zulässige Alternativen und Gegenargumente vorprüfen; Datenaufteilung und Kennzahlen kontrollieren | Keine eigenen Vorbewertungen zu Expertenlabels erklären |
| Umsetzung | Ein konkret reproduziertes Problem mit Regression und Gegenbeispiel korrigieren | Nur zugewiesene Dateien ändern; keine pauschalen Score-Anhebungen |
| Unabhängige Codeprüfung | Diff, Gegenbeispiele, Datenleckage, Import-/Exportfolgen und Tests prüfen | Konkrete Fehler melden; technische Zweitprüfung ersetzt keine Fachabnahme |

Die Codeprüfung startet nach einem überprüfbaren Implementierungsstand; sie muss nicht zugleich mit allen anderen Rollen laufen. Jeder Subagent erhält Ziel, Eingaben, erlaubte Dateien, erwartete Ausgabe und Abbruchkriterien. Alle Agenten müssen denselben Daten-/Commitstand benennen.

Standard: Daten- und Fachagenten lesen und berichten; nur ein Agent editiert eine gemeinsam verwendete Matching-Datei. Bei tatsächlich paralleler Codearbeit getrennte Git-Worktrees/Branches verwenden; der Hauptagent integriert nacheinander. Keine parallelen Änderungen derselben Datei in einem gemeinsamen Arbeitsverzeichnis. Einmal bestandene Prüfungen nur bei relevanten neuen Änderungen oder offenen Befunden wiederholen.

Falls die aktuelle Codex-Oberfläche keine Subagents bereitstellt, dieselben Rollen nacheinander oder als getrennte Codex-Aufgaben bearbeiten. Das ausdrücklich melden; keine parallele Agentenprüfung behaupten.

## Abnahme pro Pull Request

- Reproduzierbares Problem oder klar abgegrenzte Werkzeugverbesserung.
- Ein ungültiger und ein gültiger Vergleichsfall bei neuen Matching-Regeln.
- Keine Verschlechterung der bestehenden synthetischen Regressionen ohne einzeln dokumentierten, fachlich begründeten Erwartungswechsel.
- Keine neue bekannte falsche automatische Übernahme im bestätigten Prüfsatz.
- Top-1 und Recall@3 sowie falsche Vorschläge auf Fällen ohne Referenz gemeinsam betrachten. Verbesserungsziel und zulässige Abweichungen vor dem jeweiligen Experiment festlegen; keinen Zielwert erst nach Sichtung des Ergebnisses auswählen.
- Fachlich unbestätigte, unverfügbare und technisch blockierte Prüfungen sichtbar lassen.
- Relevante Tests bestehen; Originaldateien, personenbezogene Kontaktdaten, Browserdaten und Zugangsdaten gelangen nicht in den PR oder öffentliche CI-Artefakte.
- PR-Beschreibung nennt Problem, Verhalten danach, Prüfung und verbleibende Grenzen. Keine Erfolgsquote ohne benannten Prüfsatz und Nenner.

## Startprompt für eine Codex-Aufgabe

Diesen Text nach dem Basis-PR in eine neue Codex-Aufgabe mit ausgewähltem Repository kopieren. Die gewünschte Woche konkret einsetzen:

```text
Arbeite im Repository kalkprofijanek/kalkpilot-by-janek.
Lies vorhandene AGENTS.md-Anweisungen und docs/CODEX_MATCHING_AUFTRAG.md.
Bearbeite jetzt ausschließlich Arbeitspaket Woche 1 aus diesem Auftrag.

Prüfe zuerst Branch, vorhandene Änderungen, Datenzugriff und den tatsächlich
eingecheckten Ausgangsstand. Bestehende Arbeit erhalten. Fehlende Sitzungsdateien
nicht als vorhanden behandeln. Original-LVs und Prüfdaten außerhalb von Git lassen.

Nutze gezielt Subagents für unabhängige Daten-/Benchmarkprüfung und Codeprüfung,
sofern diese verfügbar sind. Du koordinierst und integrierst. Gib jedem Agenten
einen begrenzten Auftrag und eindeutige Dateizuständigkeit; keine gemeinsamen
Dateien gleichzeitig ändern lassen. Fachliche Vorbewertungen bleiben unbestätigt.

Arbeite bis zu einem konkret prüfbaren Ergebnis. Ergänze bei Regeländerungen
Regressionen und gültige Gegenbeispiele. Führe die relevanten Prüfungen aus.
Keine Preisfreigaben, keine externen KI-Uploads ohne ausdrückliche Freigabe.

Erstelle einen eigenen Branch codex/matching-w01-<kurzthema>.
Committe die zu diesem Auftrag gehörenden Dateien und pushe den Branch,
soweit der vorhandene GitHub-Zugriff dies erlaubt. Erstelle einen Draft-Pull-Request
gegen main mit Zusammenfassung, Ergebnissen und offenen Punkten. Nicht mergen.
Keine Zugangsdaten erfinden; bei fehlendem Zugriff fertigen Stand und Blocker melden.

Berichte abschließend: bearbeitete Fehler/Fälle, Datenstand, Prüfungen mit
Zählern und Nennern, offene Fragen, Branch und gegebenenfalls PR-Link.
Unterscheide lokale Änderungen, gepushten Branch und Veröffentlichung.
```

Für weitere Wochen nur die Arbeitspaketnummer und den Branchnamen anpassen. Ergebnisse vorheriger Pakete über die gemergten Dateien/PRs und den gesicherten Datenstand weitergeben, nicht nur über den Chatverlauf.

## Wie der aktuelle Stand nach GitHub kommt

### Ohne Terminal

1. Diese Codex-Aufgabe und das Repository öffnen. Den aktuellen Stand mit folgendem Auftrag abschließen: „Sichere die vorhandenen Matching-Änderungen und den Arbeitsauftrag auf einem eigenen Branch, führe die Prüfungen aus und erstelle einen Draft-PR gegen main. Original-LVs und Prüfpakete nicht hochladen. Nicht mergen.“
2. Falls die Oberfläche eine PR-Funktion anbietet, diese verwenden. Ansonsten den Agenten den Branch pushen und den PR erstellen lassen. Dafür muss die GitHub-Verbindung Schreibzugriff auf dieses Repository haben.
3. Den PR in GitHub öffnen. Unter **Files changed** die Änderungen prüfen; die Original-LVs und der Ordner `/workspace/analysis` dürfen dort nicht enthalten sein.
4. Die Browser-Regression unter **Checks** muss grün sein. Einen Draft-PR anschließend über **Ready for review** zur Prüfung freigeben und nach eigener Abnahme mergen.
5. Unter **Actions → Publish browser app** den Deploy-Schritt prüfen. Unter **Settings → Pages → Source** muss **GitHub Actions** gewählt sein. Danach https://kalkprofijanek.github.io/kalkpilot-by-janek/ öffnen und einen Pilotfall testen.

### Alternativ im Cloud-Terminal

Diese Befehle sind eine Anleitung; sie wurden durch das Erstellen dieses Dokuments nicht ausgeführt. Auf dem aktuellen lokalen Arbeitsstand vor dem Commit zunächst `git diff` prüfen. Den Branch nur neu anlegen, wenn er noch nicht existiert.

```sh
cd /workspace/kalkpilot-by-janek
git status --short
git diff --check
git switch -c codex/matching-praxisbasis
bash scripts/test-cloud.sh

git add -- KalkPilot_by_Janek.html README.md js/llm-matching.js \
  scripts/matching_originals_cloud.py scripts/matching_quality_cloud.py \
  scripts/prepare_original_review_cloud.py scripts/public_lv_review_cloud.py \
  scripts/run_public_lv_check.py config/public-lv-sources.json \
  scripts/discover_public_lvs.py tests/test_public_lv_discovery.py \
  .github/workflows/matching-check.yml tests/test_public_lv_runner.py \
  tests/fixtures/matching-quality.json tests/test_matching_workflow.py \
  tests/test_original_benchmark.py docs/MATCHING_VERTIEFUNG.md \
  docs/OEFFENTLICHE_LV_PRUEFUNG.md docs/CODEX_MATCHING_AUFTRAG.md
git diff --cached --stat
git diff --cached --check
git commit -m "Improve matching with public LV regression cases"
git push -u origin codex/matching-praxisbasis
```

Anschließend über den GitHub-Link zum gepushten Branch **Compare & pull request** öffnen und `main` als Ziel wählen. Falls die GitHub CLI bereits passend authentifiziert ist, geht es auch so:

```sh
cat > /tmp/matching-pr.md <<'EOF'
Die Fachprüfung übersieht bislang bestimmte Maß- und Tätigkeitsunterschiede;
große Referenzbestände können geeignete Kandidaten zu früh abschneiden.
Der neue Stand prüft diese Unterschiede vor der Übernahme und ergänzt
reproduzierbare Import-, Vergleichs- und Review-Werkzeuge.

Prüfung: 70 automatisierte Tests bestanden, 123 synthetische Fachfälle korrekt.
Zwei öffentliche LVs mit 829 Positionen importiert und abgeglichen;
60 Originalfälle zur unabhängigen Fachprüfung vorbereitet.
Originaldateien und Prüfpakete liegen außerhalb dieses PRs.
Die synthetischen Ergebnisse sind keine Experten-Trefferquote.
EOF

gh pr create --draft --repo kalkprofijanek/kalkpilot-by-janek \
  --base main --head codex/matching-praxisbasis \
  --title "Improve matching and add public LV review workflow" \
  --body-file /tmp/matching-pr.md
```

Die Prüfzahlen im PR-Text vor dem Senden auf den tatsächlichen letzten Lauf aktualisieren. Fehlt die Berechtigung zum Pushen, bleibt der lokale Commit erhalten; den fertigen Stand über den vorgesehenen GitHub-Zugriff oder eine Patch-Datei weitergeben. Keine Zugangsdaten in Dateien oder Chat eintragen.

## Dein laufender Aufwand

Pro Woche ein bis zwei kurze fachliche Prüftermine einplanen, beispielsweise je 30–45 Minuten. Du entscheidest anhand der vollständigen Texte über schwierige Referenzpaare und prüfst den fertigen PR. Codex übernimmt Vorbereitung, Fehlersuche, Umsetzung, technische Prüfungen und Dokumentation. Ohne diese fachlichen Entscheidungen bleibt die Arbeit ein technischer Prüflauf.
