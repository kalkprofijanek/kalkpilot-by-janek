# Erster Praxistest mit öffentlichen Leistungsverzeichnissen

Am 2. November 2026 wurden zwei öffentlich abrufbare X83-Dateien über Bekanntmachungsverweise des Bekanntmachungsservice beschafft. Originaldateien, Quellenbelege, Ranglisten und Prüfpakete liegen außerhalb des Repositories. In Git stehen ausschließlich Werkzeuge, Dokumentation und synthetische Regressionen.

## Daten und Import

| Projekt | Datei | Positionen |
| --- | --- | ---: |
| Ulm, JVA, Ersatzbau Küchengebäude – Erd-, Kanal- und Kabeltiefbauarbeiten | 26-92354 LV.X83 | 244 |
| Heidelberg, Uniklinik NUK-RADO – Spezialtiefbau, Kanal- und Druckrohrleitungsarbeiten | 26-63243-V2.X83 | 585 |

Quellen:

- [Offizieller API-Tagesexport vom 30.10.2026](https://www.oeffentlichevergabe.de/api/notice-exports?pubDay=2026-10-30&format=ocds.zip)
- [Vergabeunterlagen Ulm](https://vergabe.landbw.de/NetServer/TenderingProcedureDetails?function=_Details&TenderOID=54321-NetTender-1a1869827a0-47c5b50978d78c39&thContext=publications)
- [Vergabeunterlagen Heidelberg](https://vergabe.landbw.de/NetServer/TenderingProcedureDetails?function=_Details&TenderOID=54321-NetTender-1a0ce9295bb-46005b05fe66602c&thContext=publications)

Beide Dateien wurden durch den tatsächlichen Datei-Upload der App eingelesen. Ein unabhängiger XML-Leser vergleicht je Position Originalkennung, OZ, Titelpfad, Kurztext, Langtext, Menge und Einheit. Alle 829 Positionen und 5.803 Feldvergleiche stimmen überein; dokumentierte Einheiten-Normalisierungen wie m³ zu m3 werden berücksichtigt. GAEB-XML-Mengen wie `230.000` werden als XML-Dezimalzahl 230 gelesen, nicht als deutscher Tausenderwert.

## Aus den Daten abgeleitete Verbesserungen

| Beobachtete Situation | Änderung |
| --- | --- |
| Druckrohre mit DN/OD, Inspektionspositionen mit ID, Formstücke mit OD DN bzw. ID DN | Außendurchmesser und Innenmaße werden getrennt erkannt; bloßes DN bleibt eine andere Größe. Bereiche und „bis“-Angaben bleiben offen. |
| Grabenarbeiten im Bereich von Entsorgungsleitungen | Der Leitungsverweis wird nicht als Entsorgungstätigkeit gewertet. Verfüllen wird als Einbautätigkeit erkannt. |
| AVV mit ausgeschriebenem Klammerzusatz vor dem Schlüssel | Der Code samt gefährlichkeitsrelevantem Stern bleibt erkennbar. |
| Auflagering 60 mm gegenüber 100 mm Bauhöhe | Für Auflageringe und bestimmte Schachtbauteile werden unterschiedliche explizite Bauhöhen als Fachwiderspruch behandelt. |
| Rohrbogen 15 Grad gegenüber 45 Grad | Winkel werden bei Bogen-/Winkelpositionen separat geprüft. Mehrere Winkel und Bereiche bleiben zur Prüfung offen. |

Ein konkreter Anlass war eine 98-Punkte-Zuordnung eines 60-mm-Auflagerings zu einem 100-mm-Auflagering. Der neue Höhenvergleich begrenzt dieses Paar auf höchstens 45 Punkte. Das ist ein nachvollziehbarer Maßwiderspruch; die fachliche Gleichwertigkeit anderer Positionen folgt daraus nicht automatisch.

## Vergleich und Prüfsatz

Alle 829 Positionen wurden jeweils ausschließlich gegen das andere Projekt verglichen: 285.480 gerichtete Positionsvergleiche pro Lauf. Ein Lauf vor und ein Lauf nach den Änderungen sichern die Nachvollziehbarkeit. Preise, gelernte Zuordnungen und mitgelieferte Top-Treffer werden dabei nicht als Rangsignale verwendet.

Der erste manuelle Prüfsatz enthält 60 Fälle, je 30 pro Projekt, über die vorhandenen Kategorien verteilt. Pro Zielprojekt enthalten die Copilot-/JSON-Pakete sämtliche Referenzpositionen aus dem anderen Projekt. Der HTML-Bericht zeigt zusätzlich ausgewählte konkrete Auffälligkeiten. Die Erwartungsfelder bleiben leer und mit `unreviewed` gekennzeichnet: Es gibt noch keine unabhängig fachlich bestätigten Musterlösungen. Die Ranglisten sind Suchvorschläge, keine Entscheidungen über Passung oder Preise.

Die synthetische Regression umfasst jetzt 123 Fälle. Der gespeicherte Arbeitsstand vor diesem Praxistest klassifiziert davon 105 korrekt; der neue Stand 123. Alle 60 Browser-/Cloud-Tests bestehen. Diese Zahlen beschreiben Softwareprüfungen, keine unabhängig gemessene Trefferquote auf Kunden-LVs. Die beiden öffentlichen LVs wurden für die Entwicklung verwendet; ein unabhängiger Abschlusstest braucht weitere, zuvor ungenutzte Projekte.

## Reproduzieren

Das Manifest ist eine JSON-Liste mit `name`, absolutem `file`-Pfad und `sourceUrl` je Projekt. Dateinamen und Projektnamen müssen eindeutig sein. Die Eingabedateien liegen außerhalb des Repositories.

```sh
python3 scripts/public_lv_review_cloud.py \
  --manifest /workspace/analysis/public-lv-manifest.json \
  --output-dir /workspace/analysis/public-lv-review

python3 scripts/matching_originals_cloud.py \
  --references /workspace/analysis/public-lv-review/textreferenzen.json \
  --output-dir /workspace/analysis/public-lv-review/rankings-after \
  --review-count 60

python3 scripts/prepare_original_review_cloud.py \
  --references /workspace/analysis/public-lv-review/textreferenzen.json \
  --rankings /workspace/analysis/public-lv-review/rankings-after/holdout-rankings.json \
  --output-dir /workspace/analysis/public-lv-review/pakete \
  --count 60
```

Die öffentlichen X83-Dateien enthalten keine interne Kalkulation. Daraus werden ausschließlich Textreferenzen mit leeren Kostenansätzen erzeugt. Der Regelvergleich darf diese als D83-/X83-Textreferenzen nutzen; eine exportierbare Kalkulation oder Preisfreigabe entsteht dadurch nicht. Für den fachlichen Vergleich mit eigenen Kostenansätzen müssen anschließend unabhängig geeignete Kalkulationsreferenzen hinzukommen.
