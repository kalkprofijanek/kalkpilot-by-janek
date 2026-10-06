# Matching-Verbesserungslogik · 1.4.0 BETA

Version `1.4.0-beta` ergänzt die folgenden Matching-Verbesserungen gegenüber `1.3.2-beta`. Ziel ist die fachliche Zuordnung durch eine LLM mit nachvollziehbaren Belegen. Microsoft 365 Copilot wird über einen bewussten Dateiupload im Firmenbrowser genutzt; Codex und Claude Code bleiben über JSON nutzbar. Die App ruft keinen KI-Dienst auf und benötigt keinen API-Schlüssel.

## Umgesetzte Verbesserungen

| Verbesserung | Ergebnis |
| --- | --- |
| Fachmerkmale genauer vergleichen | Unterschiedliche Abrechnungsdimensionen, PP/PET, GRK und Flächengewicht werden geprüft. Mindestanforderungen erlauben geeignete höhere Werte. DA bleibt von DN getrennt; `75,0` und `75` sind derselbe Zahlenwert. |
| Mehrdeutigkeit sichtbar machen | Mehrere Durchmesser, unzureichend bestätigte Mindestwerte und widersprüchliche Wasser-/Abfallangaben bleiben offen. Ein gemeinsamer Wert beweist bei mehreren Leistungen keine vollständige Passung. |
| Originaltext belegen | Die KI kann je gewählter Referenz wörtliche Ziel- und Referenzauszüge zurückgeben. Erfundenes oder falsch zugeordnetes Zitat verhindert den gesamten Import. Ein gefundenes Zitat beweist noch keine fachliche Gleichwertigkeit. |
| KI-Ergebnis unabhängig prüfen | Widerspruch, unvollständig bestätigte Passung und keine erkannten Fachwidersprüche erscheinen zusätzlich zur KI-Begründung. KI-Sicherheit und Regelpunkte bleiben getrennt. Alle importierten Vorschläge sind zunächst unbestätigt. |
| Planverweise richtig behandeln | Eine Bauleistung wird nicht allein durch einen Planverweis im Langtext zur Dokumentleistung. Änderungen an Positionstexten erneuern zwischengespeicherte Profile. |
| Copilot im Firmenbrowser nutzen | Eine echte Excel-Arbeitsmappe enthält Auftrag, sämtliche Zielpositionen, sämtliche aktiven Referenzen und ein Antwortblatt. Lange Beschreibungen werden verlustfrei auf mehrere Spalten verteilt. |
| Ergebnisse zurückholen | Excel, JSON, CSV, TSV und kopierte Markdown-Tabellen laufen durch dieselbe Prüfung von Datenkennung, Vollständigkeit und Referenz-IDs. Bei Fehlern bleibt das vorherige Ergebnis erhalten. |

Die technische Prüfung erkennt bekannte Merkmale anhand von Textmustern. Sie ersetzt keine allgemeine semantische Prüfung. Insbesondere kann ein Zaun zum **Umsetzen** sprachlich ähnlich zu einem Zaun zum **Liefern und Aufstellen** sein. Die LLM muss Leistungsumfang, Nebenleistungen und Randbedingungen lesen und Unterschiede benennen. Ein hoher Punktwert allein ist kein Nachweis.

## Ablauf mit Microsoft 365 Copilot

1. In der App Referenzprojekte laden und aktivieren. Das neue GAEB-LV unter Matching laden.
2. **Microsoft 365 Copilot · Excel** auswählen und **Copilot-Excel herunterladen** anklicken.
3. Im freigegebenen Microsoft-365-Copilot-Browser die Datei hochladen und den folgenden Auftrag einfügen.
4. Die ausgefüllte Arbeitsmappe mit dem Blatt **Antwort** herunterladen. Falls Copilot keine Datei erzeugt, die vollständige Antworttabelle kopieren und in der App einfügen.
5. Antwort importieren. Fachliche Hinweise prüfen und gewünschte Referenzvorschläge bewusst übernehmen. Preisfreigabe bleibt ein separater Arbeitsschritt.

```text
Bearbeite den Matching-Auftrag in dieser Exceldatei.
Lies das Blatt Auftrag sowie alle Langtext-Spalten der Zielpositionen
und Referenzen. Vergleiche Leistungsumfang, Material, Maße, Einheit,
Ausführungsverfahren, Nebenleistungen und Randbedingungen.
Wähle nur vorhandene ReferenzIDs. Ein fehlender Treffer ist zulässig.
Fülle für jede ZielID genau eine Zeile im Blatt Antwort aus.
Behalte requestId und ZielID unverändert. Gib Unterschiede und offene
Angaben an. Liefere für den ersten Vorschlag wörtliche Belege aus
Ziel- und Referenztext. Erfinde keine Zitate, Referenzen oder Preise.
Gib die Exceldatei mit ausgefülltem Antwortblatt zurück, alternativ
die gesamte Antworttabelle als TSV oder Markdown einschließlich Kopfzeile.
Wenn du nicht alle Positionen und Referenzen vollständig lesen kannst,
sage das ausdrücklich; liefere keine scheinbar vollständige Bewertung.
```

Der tatsächliche Copilot-Zugang wurde hier nicht getestet. Dateierstellung, vollständiges Lesen großer Tabellen und Ausgabelimits hängen von der im Unternehmen bereitgestellten Oberfläche ab. Eine vollständige Antwort ist technisch überprüfbar; ob Copilot alle Referenzen gelesen hat, lässt sich damit nicht beweisen. Bei einem Limit soll als nächster Schritt eine kontrollierte Aufteilung nach Zielpositionen ergänzt werden, jeweils mit allen aktiven Referenzen und eindeutiger Datenkennung. Ein stiller Ausschnitt der besten Texttreffer würde die KI-Auswahl unnötig einschränken.

## Verbesserungslogik für weitere Iterationen

1. **Fehler sammeln:** Zielposition, vollständige Vergleichstexte, falsche Auswahl und fachlichen Grund festhalten. Beispiel: gleiches Kurztextwort, aber anderer Durchmesser oder anderer Leistungsumfang.
2. **Erwartung bestätigen:** Ein fachlich bestätigtes Referenzpaar, zulässige Alternativen oder ausdrücklich kein Treffer bilden den Prüfmaßstab. Eine KI-Antwort oder die Übernahme eines ungeprüften Preises wird nicht automatisch zum richtigen Beispiel.
3. **Gegenbeispiel ergänzen:** Zu jedem neuen Ausschluss gehört ein gültiger Fall. Beispiel: GRK 2 für mindestens GRK 3 ablehnen, GRK 4 für mindestens GRK 3 erhalten. Dadurch werden neue Regeln nicht pauschal strenger.
4. **Gezielt ändern und wiederholen:** Fachmerkmale, Auftrag oder Darstellung ändern; denselben Datenbestand vor und nach der Änderung prüfen. Testdaten und Modell/Prompt-Version nachvollziehbar halten.
5. **Unabhängig bewerten:** Für ein weiteres Pilot-LV darf dessen eigenes Referenzprojekt nicht im Vergleichsbestand sein. Ein Fachprüfer bewertet die Zuordnungen, bevor diese Daten zur späteren Entwicklung genutzt werden.
6. **Erst dann freigeben:** Weniger falsche Passungen, erhaltene richtige Passungen und korrekte Meldungen fehlender Referenzen sind die Kriterien. Höhere Durchschnittspunkte allein sind kein Qualitätsgewinn.

Ein künftiger fachlich bestätigter Prüfsatz soll mindestens Rohrleitungen, Vlies, Abfall, Erdbau, Transport, Bauzaun und Stundenlohn abdecken. Gemessen werden korrekte erste Vorschläge, zulässige Alternativen, übersehene vorhandene Treffer und fälschlich vorgeschlagene Treffer bei fehlender Referenz. Preise werden separat bewertet. Änderungen am Datenbestand oder an den KI-Anweisungen erfordern einen erneuten Vergleich.

## Bisherige Prüfung

- **41 automatisierte Tests bestanden**, einschließlich vorhandener Browser-/Cloud-Prüfungen, Fachmerkmalen, Textbelegen, Excel-Rückimport, kopierter Tabelle, beschädigtem Archiv und atomarer Ablehnung ungültiger Antworten.
- **24 gezielt formulierte fachliche Prüffälle:** alte Merkmalsprüfung klassifiziert 15 korrekt, neue Merkmalsprüfung 24. Das sind synthetische Regressionen gegen bekannte Fehler, keine unabhängige Erfolgsquote der LLM.
- **Originaldaten außerhalb des Repositories:** Excel mit 165 Eisert-Positionen und 1.360 Referenzen aus drei anderen Projekten, rund 2,94 MB. Eine unabhängige Excel-Bibliothek konnte alle vier Blätter und Zeilen lesen.
- **Acht Original-Pilotpositionen:** fachlich geprüfte Agenten-Auswahl mit Textbelegen; zwei passend, drei mit Einschränkungen, drei ohne belastbaren Treffer. Die App validiert fünf Referenzvorschläge, bestätigt automatisch null Positionen und null Preise. Dies ist eine Ablaufprobe, keine Bewertung von Microsoft 365 Copilot.
- Der Bauzaun-Planverweis führte vorher zum falschen Dokumentabzug auf 39 Punkte. Dieser Abzug entfällt; verbleibende Unterschiede müssen weiterhin fachlich geprüft werden.

Reproduzierbar im Cloud-Terminal:

```sh
bash scripts/test-cloud.sh
.venv/bin/python scripts/matching_quality_cloud.py \
  --baseline-ref 37fdaf1 \
  --output-dir /workspace/analysis/matching-quality
```

Der zweite Befehl verwendet ausschließlich synthetische Fälle. Originaldaten, individuelle KI-Antworten und Excel-Prüfdateien gehören nicht ins öffentliche Repository. Änderungen werden als Pull Request geprüft. Nach einem Merge in main veröffentlicht der Pages-Workflow die getestete App.
