# Browser-Umbau und Kalkulations-BETA

Stand: 5. Oktober 2026. Ziel: KalkPilot auf einem Firmenrechner als statische Browser-App verwenden, mit manuellen Datei-Uploads in ChatGPT. Kein lokales Programm, API-Zugang oder Server für die Kalkulationsdaten erforderlich.

## GitHub-Recherche und Entscheidungen

Die öffentlichen Repository-READMEs, ausgewählte Lizenzdateien und npm-Paketmetadaten wurden direkt abgerufen. Während der ersten Recherche war die GitHub-API gesperrt; sie ist inzwischen erreichbar. Die ursprünglichen Bibliotheksversionen beziehen sich auf die abgerufenen Paketmetadaten. OpenConstructionERP wurde ergänzend auf einem festen Commit untersucht; Quellen, Lizenzbewertung und konkrete Lücken stehen im [Architekturabgleich](ARCHITEKTURABGLEICH.md).

| Projekt | Geprüfte Paketversion / Lizenz | Nutzen | Entscheidung |
| --- | --- | --- | --- |
| [Dexie.js](https://github.com/dexie/Dexie.js) | 4.4.6 / Apache-2.0 | IndexedDB mit Transaktionen und Schema-Versionen; für große lokale Referenzdaten | Jetzt eingebunden, unveränderte Distribution lokal, Lizenz/NOTICE und SHA-512-Provenienz enthalten |
| [MiniSearch](https://github.com/lucaong/minisearch) | 7.2.0 / MIT | Volltextindex mit Präfix-/Fuzzy-Suche in modernen Browsern | Für Kandidatensuche vormerken; zuerst gegen vorhandene Suchfenster messen. Keine fachlichen Regeln ersetzen |
| [decimal.js](https://github.com/MikeMcl/decimal.js) | 10.6.0 / MIT | Dezimalarithmetik für nachvollziehbare Geldrechnung | Für den geprüften Kalkulationskern vormerken. Präzise Arithmetik ersetzt nicht die Prüfung der iTWO-Faktorsemantik |
| [Fuse.js](https://github.com/krisk/Fuse) | 7.5.0 / Apache-2.0 laut Paketmetadaten | Unscharfe Suche | Alternative zu MiniSearch; nicht beide zusätzlich einbauen, bevor ein echter Vergleich Nutzen zeigt |
| [fast-xml-parser](https://github.com/NaturalIntelligence/fast-xml-parser) | 5.11.2 / MIT | XML-Objektmodell | Browser-DOMParser zunächst behalten; eine XML-Bibliothek liefert weder GAEB-Fachsemantik noch automatische Schema-Konformität |

Die GitHub-Suche nach GAEB/JavaScript ergab in den zugänglichen Ergebnissen keinen geprüften Kandidaten, der die beobachteten D83-, X83- und iTWO-Probleme nachweislich vollständig löst. Deshalb wird kein unbekannter Parser übernommen. Das ist keine Aussage, dass solche Projekte grundsätzlich nicht existieren.

## Umgesetzt

- Große Referenzen atomar in IndexedDB speichern; vorhandene Daten bei ungültigem Import oder fehlgeschlagenem Speichern erhalten. Alte localStorage-Daten werden übernommen, ohne die ursprünglichen Kopien zu löschen.
- Speicherstatus sichtbar machen; portable JSON-Sicherung beibehalten. Alle Referenzmutationen warten auf die anfängliche Wiederherstellung.
- D83-Positionsnummern bis zu den Positionskennzeichen lesen statt auf acht Zeichen zu beschränken; doppelte/unbekannte Nummernstrukturen melden.
- D83-Strukturzeilen 31/32 nicht als EP behandeln. Diese DA83-Dateien sind keine verifizierte Preisquelle. Historische Festpreisfelder in bereits gespeicherten Referenzen werden nicht blind gelöscht; sie sind separat gegen Originale zu prüfen.
- UTF-8, Windows-1252 und DOS CP850 für Textdateien unterstützen, mit manueller Auswahl für unklare Fälle. Die automatische Erkennung ist eine Heuristik, keine universelle Formatgarantie.
- X83-Kompatibilitätsimport für Description/S und Description/L ergänzen. Dadurch ist die vorliegende Trioxan-Textstruktur lesbar; XSD-Konformität wird damit nicht behauptet.
- Verknüpfte D83-Langtexte in Leistungsprofil, Kategorie- und Konflikterkennung einbeziehen.
- Unaufgelöste Assembly-Preise als Risiko anzeigen und automatische Übernahme unterbinden.
- Direkte Anthropic-API-Anbindung entfernen. Ein manuell herunterladbares JSON-Prüfpaket enthält Zielpositionen, Kandidaten, historische Ansätze, Faktoren, Risiken und klare BETA-Kennzeichnung. Es setzt weder Preise noch Übernahmen automatisch.
- Browsermodule für Speicherung, Encoding und Prüfpaket auslagern; Regressionen und GitHub-Actions-Prüfung ergänzen.
- Startbedingungen und Matching verwenden denselben Referenzpool. Reine D83-Textreferenzen schalten den Start bei aktiviertem Textvergleich frei; fehlende Voraussetzungen und fehlgeschlagene LV-Imports werden sichtbar erklärt. X83-XML mit Namespace-Präfix ohne XML-Deklaration wird erkannt.
- Matching-Punktzahlen einheitlich abschließen: erkannte Fachdeckel können weder durch verknüpfte D83-Treffer noch durch Projektboni überschritten werden, auch in der manuellen Suche. Angezeigte Endpunktzahl und Debugdaten stimmen überein.
- Prüfschritte und Datenqualität in Detailansicht und ChatGPT-Paket anzeigen; fehlende/ungültige Kostenwerte melden. Historische Preise, Preisstand und Region gelten weiterhin als nicht bestätigt.
- [Öffentliche App](https://kalkprofijanek.github.io/kalkpilot-by-janek/) über den getesteten Pages-Workflow veröffentlichen; Link und [Release-Anleitung](VEROEFFENTLICHUNG.md) ergänzen.

## Echtes LLM-Matching in der Cloud

Codex/Claude Code ordnet Zielpositionen selbst konkreten Referenzen zu. Ein Matching-Paket enthält den gesamten aktiven Referenzbestand; eine geprüfte Antwort-JSON übernimmt konkrete IDs und Begründungen in die App. Alle Zuordnungen starten zur fachlichen Prüfung. Das Cloud-Werkzeug startet die echte Browser-App, bereitet den Auftrag vor und validiert die Antwort; die LLM trifft die semantischen Entscheidungen zwischen diesen Schritten. [Ablauf und Agenten-Auftrag](LLM_MATCHING.md).

## Ergänzung aus der ChatGPT-Info

Der [Architekturabgleich](ARCHITEKTURABGLEICH.md) prüft die vorgeschlagene OpenConstructionERP-Referenz, die aktuelle KalkPilot-Architektur und die Lücken. Bestätigte Ergänzungen:

- Browserbasierte Entwicklung ausdrücklich zusätzlich zur Browserbedienung vorbereiten: Cloud-Start-/Prüfbefehle und eine GitHub-Codespaces-Devcontainer-Konfiguration sind im Nachtrag ergänzt. Der weitergeleitete Entwicklungsport soll privat bleiben. Auf dem Firmenrechner müssen keine Entwicklungswerkzeuge installiert werden.
- Kandidatensuche, Leistungs-/Einheitenprüfung und Preisplausibilität als nachvollziehbare Pässe planen. Exakte Treffer, Lern- und Projektboni dürfen fachliche Sperren für automatische Übernahmen nicht umgehen.
- Ähnlichkeit, Datenvollständigkeit, fachliche Übertragbarkeit und Freigabe getrennt führen. HIGH/MEDIUM/LOW sind zunächst Prüfklassen, keine bewiesenen Wahrscheinlichkeiten oder Preisfreigaben.
- Historische Daten um versionierte Herkunft, bestätigten Preisstand/Region und Review-Entscheidungen erweitern. Nullpreise und fehlende Metadaten bleiben ungeklärt; Preis-Ausreißer nur unter wirklich vergleichbaren vollständigen Ansätzen beurteilen.
- Bestehendes GitHub Pages beibehalten: Der Workflow Publish browser app prüft und veröffentlicht main über GitHub Actions. Ein anderer Hostinganbieter ist derzeit nicht erforderlich. Codespaces und Produktionsseite teilen wegen verschiedener Website-Ursprünge keinen lokalen Referenzspeicher.

OpenConstructionERP ist AGPL-3.0. Sein Quellcode wird nicht übernommen; es dient als geprüfte Architektur-Referenz. Produktive Provider-APIs und Vektordatenbanken bleiben optionale spätere Entscheidungen. Der festgelegte manuelle ChatGPT-Upload-Workflow bleibt die aktuelle Zielarchitektur.

Die konkreten Befehle und der Cloud-/Codespaces-Ablauf stehen in der [Cloud-Anleitung](CLOUD_ENTWICKLUNG.md). Alle Installationen laufen auf der Cloud-Maschine; die Anwendung bleibt statisch und API-frei. Neue Codespaces und die tatsächliche Firmenbrowser-Vorschau sind separate Abnahmen.

## Nächste Ausbaustufen mit Abnahmekriterien

### A. Referenzqualität und Kandidatensuche

Einheiten, Preisstand, Region, Quelle und Bausteinauflösung getrennt erfassen. Titelkontext und „wie Pos.“-Verweise auflösen; ergänzende Kurz-/Langtextdateien erkennen, bevor sie als unabhängige Referenzen importiert werden. MiniSearch nur dann einsetzen, wenn es bei realen, fachlich bestätigten Fällen die Kandidatenabdeckung oder Laufzeit verbessert.

Abnahme: gemeinsam bewertete echte Soll-Treffer; projektweise Trennung von Testfällen und nahezu identischen Referenzen; getrennte Messung von Top-1/Top-3, Kandidatenabdeckung und falschen automatischen Übernahmen. Vier Referenzprojekte erlauben noch keine belastbare universelle Qualitätsbehauptung.

### B. Geprüfter Kalkulationskern

Verschachtelte SubItems und Assembly-Verweise vollständig auflösen; Faktor, Leistungsfaktor, Mengenbezug, deaktivierte Ansätze, Zu-/Abschläge und Ressourcenpreise fachlich korrekt abbilden. Historischen vereinfachten Referenzwert, bestätigten Referenz-EP und neu berechneten Angebotspreis trennen. decimal.js kann dabei Rundung und Dezimalrechnung übernehmen.

Abnahme: repräsentative Positionen mit bestätigtem iTWO-Ergebnis für einfache Ressource, Leistungsfaktor, Baustein, deaktivierten Ansatz, Pauschale und negative Position. Ohne Ressourcen-/Bausteinkatalog und bestätigte Ergebnisse bleiben Preise unvollständig. Ein Nullpreis darf keine fehlende Preisauflösung ersetzen.

### C. Selbstständiger Kalkulationsentwurf · BETA

Erste Leistungsfamilie anhand vollständig vorhandener Ansätze auswählen, z. B. Asphaltfräsen. Geeignete Referenzbausteine vorschlagen, Mengen/Leistungsansätze anpassen, feste und variable Kosten unterscheiden und Transport/Entsorgung nicht doppelt ansetzen. Fehlende Inputs als gezielte Rückfragen zeigen. Ein ChatGPT-Modell kann die vom Nutzer hochgeladenen Dateien strukturieren und erläutern; die geprüfte Rechenlogik muss die Geldbeträge bestimmen.

Abnahme: jeder Ansatz zeigt Herkunft, Änderungen und offene Annahmen. Status pro Position: Unvollständig / Zur Prüfung / fachlich geprüft. Die aktuelle ChatGPT-Prüfpaketfunktion ist die Vorbereitung dieses Workflows, noch kein solcher vollständiger Kalkulationskern.

### D. Export und Veröffentlichung

Vor Export eine Auswahlübersicht mit Ziel-OZ, Referenz-OZ, Quelle, Rohkopie/Fallback und offenen Kalkulationspunkten anbieten. Exportversionen semantisch vergleichen; die vorgelegten V1/V2-Dateien haben unterschiedliche Positionsauswahlen und sind kein reiner Formatvergleich.

Abnahme: geprüfter iTWO-Reimport, keine unerklärten Positionswechsel, nachvollziehbare Struktur und Faktoren. Danach BETA-Version über den bestehenden statischen Veröffentlichungsweg bereitstellen und mit einem repräsentativen Firmenbrowser prüfen. Ein erfolgreicher Git-Push oder Pull Request ist noch keine Veröffentlichung.

## Firmenbrowser und Datenschutz im Arbeitsablauf

- Alle Laufzeitbibliotheken werden lokal von derselben Website geladen. Keine CDN- oder KI-API-Abhängigkeit.
- ChatGPT-Uploads erfolgen ausschließlich vom Nutzer im Browser. Ein ChatGPT-Login ersetzt keinen API-Zugang; dieser Workflow benötigt keinen API-Zugang.
- Browserdaten sind an Profil und Website-Adresse gebunden. Die JSON-Sicherung ist der portable Weg; einen Wechsel der Adresse oder das Löschen von Firmendaten berücksichtigen.
- Original-LVs und Referenzdaten bleiben außerhalb von Git. Tests verwenden synthetische Beispiele.
- Der vollständige statische Ordner einschließlich js/ und vendor/ muss online gestellt werden. Die bisherige Ein-Datei-Verteilung wird nicht mehr vorausgesetzt.

## Validierung und Grenzen

Die Regressionen prüfen bestehende Matching-/Exportformat-/Speicher-Selbsttests, breite D83-OZ, Strukturzeilen ohne erfundene EP, Encoding, X83-Kompatibilität, Langtext-Konflikte, große IndexedDB-Daten über Neuladen, fehlgeschlagene Imports/Saves, Altdatenmigration und manuelle ChatGPT-Downloads ohne externe Netzaufrufe.

Zusätzlich werden die 26 bereitgestellten Originaldateien lokal gegen die Importfunktionen geprüft. Diese Dateien werden nicht eingecheckt. Externe iTWO-Validierung, Prüfung am tatsächlichen Firmenrechner und allgemeine Kalkulationsgenauigkeit bleiben gesonderte Abnahmen.

### Ergebnisse der aktuellen Umsetzung

- 12 Browser-Regressionsprüfungen bestanden; darin 136 Matching-Fälle, drei Exportformat-Fälle und beide bestehenden Speicher-/Entscheidungs-Selbsttests.
- Alle 26 zusätzlichen Dateien lokal durch die Importfunktionen geprüft. Trioxan: 82 statt null Positionen. Büttelborn: 90 Positionen ohne doppelte kanonische OZ. D83-Imports: keine EP aus Strukturzeilen.
- Original-JSON: vier Projekte / 1.527 Positionen nach Import und erneut vier Projekte nach Neuladen; keine JavaScript-Seitenfehler. Importdauer in dieser Umgebung etwa 2,4 Sekunden.
- Synthetischer Ranking-Test: 26/26 Top-1, kein Beleg für allgemeine Qualität auf neuen Projekten.
- Der betriebliche Edge-/Chrome-Browser und ein iTWO-Reimport wurden nicht extern geprüft. Vollständige selbstständige Preisberechnung bleibt die oben beschriebene nächste Ausbaustufe.

### Ergebnisse des Cloud-Nachtrags

Die neuen Cloud-Skripte sind in der bestehenden Codex-Maschine getestet; das Setup ist wiederholbar. Alle 25 Regressionstests bestehen, einschließlich drei neuer Prüfungen für Start/Healthcheck/Dateibereitstellung. Die Devcontainer-Konfiguration wurde gegen die offizielle Basisspezifikation validiert. Neue Codespaces und der externe Firmenbrowser bleiben separat zu prüfen; produktive API-Aufrufe werden durch den Nachtrag nicht eingeführt.
