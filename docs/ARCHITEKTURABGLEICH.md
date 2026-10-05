# Prüfung der zusätzlichen ChatGPT-Empfehlungen

Stand: 5. Oktober 2026. Grundlage sind der bestehende KalkPilot-Branch und das untersuchte OpenConstructionERP. Der eingesandte Text ist eine Sammlung zu prüfender Vorschläge; er ersetzt nicht die vereinbarte Nutzung über Browser und manuelle ChatGPT-Uploads. In diesem Nachtrag werden Analyse und Planung ergänzt sowie Cloud-Startskripte und eine Codespaces-Konfiguration vorbereitet. Eine produktive API oder Server-Datenbank wird nicht eingebaut.

## Ergebnis und Prioritäten

Die Empfehlungen zur Cloud-Entwicklung, mehrstufigen Prüfung, nachvollziehbaren Kandidaten, historischen Daten und menschlicher Freigabe sind relevant. Eine vollständige ERP-Übernahme, produktive LLM-API, PostgreSQL oder ein Vektordienst ist für den aktuellen Browser-Workflow nicht erforderlich. Der bereits funktionierende KalkPilot wird schrittweise weiterentwickelt.

| Empfehlung | Prüfung am aktuellen Stand | Entscheidung |
| --- | --- | --- |
| Entwicklung, Tests und Bedienung im Firmenbrowser | App läuft statisch; Cloud-Tests und PR-Workflow existieren. Codespaces-Konfiguration ist in diesem Nachtrag vorbereitet; ein frischer Codespace wurde noch nicht gestartet. | Start-/Prüfskripte und Devcontainer ergänzt; Werkzeuge laufen in der Cloud, nicht auf dem Firmenrechner |
| OpenConstructionERP als Referenz | Lizenz und relevante Backend-/Frontend-Dateien geprüft | Architekturprinzipien berücksichtigen; keinen Quellcode übernehmen |
| Multi-Pass Matching | ERP besitzt explizite semantic/unit_scale/rate_sanity-Pässe; KalkPilot hat Kandidatensuche und Fachprüfungen, aber keine vollständige getrennte Pipeline | Eigenständiges Prüfprotokoll und klar getrennte Stufen planen |
| Mehrere Kandidaten mit Begründung | KalkPilot zeigt bis zu drei Kandidaten, Alternativen, Debugwerte und Risiken | Erhalten; Metadaten, Prüfstatus und Herkunft ergänzen |
| HIGH/MEDIUM/LOW/NO MATCH | Vorhandene Farbstufen beruhen auf Scores; diese sind keine kalibrierten Wahrscheinlichkeiten | Evidenzbasierte Prüfklassen ergänzen; Beispielschwellen des Textes nicht ungeprüft übernehmen |
| Vektor-/Hybrid-Suche | Regel-, Token-, Synonym-, Fuzzy- und Exact-Suche vorhanden; kein Backend und keine relationale Datenbank | Zuerst lokale Kandidatensuche gegen echte Soll-Treffer messen; Embeddings erst bei nachgewiesenem Recall-Problem |
| Provider-Abstraktion und API-Secrets | Widerspricht dem festgelegten reinen Datei-Upload-Workflow | Optionaler späterer Ausbau nach eigener Entscheidung; aktuell weder Provider-Aufrufe noch API-Schlüssel |
| Erweiterbares historisches Datenmodell | Projekte/Positionen/Kosten/Original-XML und Lernsignaturen vorhanden; Preisstand/Region/Freigaben nicht konsistent vorhanden | Versioniertes Datenmodell mit nachvollziehbarer Herkunft und unbekannten Feldern planen |
| Preisbildung aus realen Ansätzen | Grundsätzlich passend; aktuelle EP-Anzeige ist vereinfacht, Bausteine teils unaufgelöst | Geprüften Kalkulationskern priorisieren; keine Preisfindung allein durch ChatGPT |
| Deployment aus GitHub | GitHub Pages ist bereits eingerichtet, Quelle main und Repository-Wurzel | Bestehenden statischen Weg beibehalten; Cloud-Anbieterwechsel erst bei zusätzlichem Backendbedarf |

## A/B/E/F: KalkPilot heute und konkrete Lücken

`KalkPilot_by_Janek.html` enthält Oberfläche, Parser, Referenzverknüpfung, Matching, Lernspeicher und XML-/CSV-Export. `KalkPilot_Referenzpaket_Builder.html` erstellt Referenzpakete. Die neuen Module `js/reference-store.js`, `js/gaeb-encoding.js` und `js/browser-review.js` übernehmen lokale Speicherung, Decodierung und den manuellen KI-Austausch. Dexie ist lokal eingebunden; kein Build oder Produktivserver ist erforderlich.

| Bereich | Vorhandene Dateien/Funktionen | Noch erforderlich |
| --- | --- | --- |
| Import | parseD83, parseP83, parseGAEBXML, parseXML, mergeD83andXML | Weitere Format-/Schemafälle, Importbericht, Versions-/Dublettenerkennung und verlässlicher Titelkontext |
| Merkmale | buildPositionMatchProfile, Kategorie, EBV/DepV, Leistungsrichtung, Einheit und Menge | Vollständige Herkunft der Merkmale; unbekannte Angaben, Preisstand und Ausführungsparameter sichtbar machen |
| Kandidaten | buildReferenceBuckets, getBucketCandidates, candidateQuickScore, collectAutoRecallCandidates | Kandidatenabdeckung messen; Suchindex erst nach Vergleich auswählen |
| Ranking | calcScore, linkedD83MatchScore, Projekt-/Lernsignale, hardCapsApplied | Erklärbare Stufen und konsistente Endbewertung nach sämtlichen Boosts; Direktverknüpfungen müssen aktuelle Fachkonflikte sichtbar erhalten |
| Prüfung/Entscheidung | getMatchRiskReasons, canAutoAcceptMatch, applyStoredMatchDecisions, manuelle Auswahl | Auswahl, fachliche Prüfung und Preisfreigabe als unterschiedliche Zustände; manuelle Overrides protokollieren |
| Kalkulation | Historische Kostenzeilen, Faktoren, SubItems und Roh-XML | Bausteinauflösung und bestätigte iTWO-Rechenregeln; Ressourcenpreise und verifizierte EP/GP |
| Historie | Top-Treffer, Ablehnungen und Exporthistorie | Fachlich bestätigte Entscheidungen mit Version, Begründung und Bezug zur unveränderten Quelle |
| Entwicklung | Python-Webserver in der Cloud, requirements-dev.txt, Browser-Regressionssuite und GitHub Actions | Neue scripts/dev.py, scripts/setup-cloud.sh, scripts/test-cloud.sh, scripts/check_ready.py und Devcontainer prüfen; frischen Codespace gesondert abnehmen |

Der monolithische Hauptteil wird an Schnittstellen schrittweise ausgelagert. Die bestehenden Parser, Exporte und Fachregeln werden über Regressionen erhalten; kein großer Rewrite ist geplant.

## C/D/H: Was OpenConstructionERP tatsächlich enthält

Untersucht wurde Commit `4557c8939fd7b3285002836b282014fa1cc65449`. Das Repository war am Prüftag nicht archiviert. Die Lizenzdatei nennt **GNU Affero General Public License, Version 3**; die GitHub-Metadaten bestätigen AGPL-3.0.

Quellen am festen Commit:

- [Lizenz](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/LICENSE).
- [ai_estimator/service.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/modules/ai_estimator/service.py): `_map_group`, `_pass_semantic`, `_reconcile_units`, `_rate_sanity`; echte Kandidaten, Einheiten-/Dimensionsprüfung, Ausreißermarkierung und nachvollziehbare Stufen.
- [match_service/envelope.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/core/match_service/envelope.py): Kandidatenmodell, Projektkontext und Confidence-Bänder. Diese Regeln sind Heuristiken, keine nachgewiesene KalkPilot-Genauigkeit.
- [match_service/ranker_qdrant.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/core/match_service/ranker_qdrant.py): Kandidaten-Ranking und Suchkontext.
- [costs/buildup.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/modules/costs/buildup.py) und [resource_pricing.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/modules/costs/resource_pricing.py): Unterscheidung Katalog-/Komponentenpreis und regionale Ressourcenpreise. Diese Regeln sind keine iTWO-Implementierung und dürfen nicht als Ersatz der iTWO-Validierung behandelt werden.
- [core/vector_index.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/core/vector_index.py) und [costs/vector_adapter.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/modules/costs/vector_adapter.py): Embedding-/Index-Schnittstellen, LanceDB-/Qdrant-Anbindung, Metadaten und Verhalten bei fehlenden optionalen Diensten.
- [ai/ai_client.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/app/modules/ai/ai_client.py): mehrere Provider. Eine solche Schicht ist für KalkPilot derzeit nicht nötig.
- [MappingTrace.tsx](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/frontend/src/features/ai-estimator/components/MappingTrace.tsx), [AlternativesDrawer.tsx](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/frontend/src/features/ai-estimator/components/AlternativesDrawer.tsx) und [Stage4Review.tsx](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/frontend/src/features/ai-estimator/components/Stage4Review.tsx): sichtbare Prüfstufen, Alternativen und ausdrückliche menschliche Freigabe.
- [test_mapping_passes.py](https://github.com/datadrivenconstruction/OpenConstructionERP/blob/4557c8939fd7b3285002836b282014fa1cc65449/backend/tests/unit/ai_estimator/test_mapping_passes.py): isolierte Tests für Einheitenkonflikte und Preis-Ausreißer. Sie verwenden kuratierte Kandidaten und sind kein Beleg für die Genauigkeit auf unseren LVs.

Es wurde kein AGPL-Quellcode, Testcode, UI-Text oder Ressourcenbestand in KalkPilot übernommen. Übernommen werden sollen allgemeine Architekturprinzipien und eigenständig entworfene Verträge. Eine direkte Übernahme oder abgeleitete Portierung würde eine gesonderte Lizenzprüfung und Entscheidung erfordern; bloßes Umbenennen oder Übersetzen beseitigt Lizenzpflichten nicht. Aus der AGPL folgt nicht pauschal, dass jede daneben genutzte oder verlinkte unabhängige Komponente automatisch dieselbe Lizenz erhält.

Die Behauptung zur öffentlichen Verfügbarkeit von Appius-Quellcode wurde in dieser Prüfung nicht unabhängig untersucht. Das Zielbild transparenter Referenzvorschläge benötigt keinen Appius-Code.

## G/I: Zielarchitektur für den vereinbarten Browserbetrieb

Der Laufzeitpfad bleibt: Dateiimport → versionierter lokaler Referenzbestand → Leistungsmerkmale → mehrere Kandidaten → fachliche Prüfung → gegebenenfalls Preisplausibilität → begründeter BETA-Vorschlag → menschliche Prüfung → Export. ChatGPT wird über ein vom Nutzer heruntergeladenes Prüfpaket eingebunden; seine Antwort ist zunächst eine Notiz, keine automatisch ausführbare Änderung.

### Eigenständige Matching-Pässe

1. **Kandidatensuche:** Exakte und normalisierte Texte, Token/Synonyme/Fuzzy, Einheit und Klassifikation kombinieren. Alle Kandidaten behalten Quell-ID und Quellversion. Embeddings sind eine mögliche spätere zusätzliche Suchquelle, keine Preisquelle.
2. **Leistungs-/Einheitenprüfung:** Fachmerkmale und Dimensionen deterministisch vergleichen. Normalisierung von Schreibweisen ist von tatsächlicher Umrechnung zu unterscheiden. t↔m3 benötigt Dichte, m2↔m3 benötigt Dicke und Zeit-/Vorhalteansätze benötigen passende Dauer; fehlende Parameter werden nicht geschätzt. Lern- und Projektboni dürfen Sperren für die automatische Übernahme nicht umgehen.
3. **Preis-/Mengenprüfung:** Nur vollständig aufgelöste und vergleichbare Kalkulationen prüfen. Gleiche Währung, Einheit, Mengenbezug, Preisstand, Region und Leistungsumfang berücksichtigen. Ausreißer kennzeichnen und Alternativen erhalten. Ein Median aus wenigen, duplizierten oder unvollständigen Referenzen ist kein zuverlässiger Marktpreis. Fehlen geeignete Daten, lautet das Ergebnis „nicht geprüft“, nicht „plausibel“.
4. **Prüfklasse und Freigabe:** Ähnlichkeit, Datenvollständigkeit, Übertragbarkeit und Prüfergebnis getrennt ausweisen. HIGH bedeutet einen gut belegten Vorschlag, keine automatische Preisfreigabe; MEDIUM verlangt Prüfung; LOW und NO MATCH erlauben keine automatische Kalkulationsübernahme. Fachlich bestätigte Testfälle bestimmen die späteren Schwellen. Eine Zahl wie 0,92 aus dem eingesandten Beispiel wird nicht als kalibrierte Wahrscheinlichkeit übernommen.

Jeder Pass soll Kandidatenzahl, verwendete Merkmale, Ausschluss-/Warnungsgründe und Datenstand festhalten. Die Anzeige muss zwischen hoher Textähnlichkeit und einem ungeklärten Fachkonflikt unterscheiden, auch wenn Direktverknüpfung oder Projektbonus den derzeitigen Score erhöhen.

### Historisches Datenmodell

In einer nächsten Schema-Version getrennte Entitäten für Projekt, Position, Kalkulationsansatz, Ressourcenpreis und Prüfentscheidung vorsehen; Originaldatei/-XML unverändert referenzieren. Bestehende JSON-Sicherungen müssen migrierbar bleiben.

- Projekt: stabile ID, Version, Name, Projektart, optional Kunde/Region, Währung und Preisstand.
- Position: Quell-ID/-version, OZ, Titelpfad, Kurz-/Langtext, Einheit, Menge und strukturierte Leistungsmerkmale wie Material, EBV/DepV, Entsorgungsweg, Entfernung oder Schichtdicke.
- Kalkulation: vollständige Hierarchie, Geräte/Personal/Material/NU, Faktoren, Zuschläge und getrennte Felder für vereinfachten Referenzwert, bestätigten EP/GP und neuen Entwurf.
- Herkunft pro Feld: Originalangabe, deterministisch extrahiert, vom Nutzer bestätigt oder KI-Vorschlag. Unbekannte Werte bleiben leer; ein Dateiname ersetzt keinen bestätigten Preisstand.
- Prüfentscheidung: Objekt-/Kalkulationsversion, Status, Entscheidung, Zeitpunkt und Begründung. Auswahl oder Export allein ist kein Nachweis fachlicher Freigabe. Änderungen nach Freigabe müssen den Prüfflag zurücksetzen.

Personen-, Kunden-, Lieferanten- und Anlagendaten nur ergänzen, wenn sie für den gewählten Workflow tatsächlich gebraucht werden. Die vorgeschlagene vollständige Feldliste ist ein Erweiterungsrahmen, keine Pflicht, fehlende Daten zu erfinden.

### Suche und Infrastruktur

Für die aktuelle lokale Referenzbibliothek zuerst IndexedDB und vorhandene Suche verwenden. MiniSearch ist der bereits bewertete mögliche Zusatzindex. Ein lokales Embedding-Modell wäre ein späterer Vergleichskandidat; Modellgröße, Browserleistung, Firmennetzfreigaben, Lizenz und Datenübertragung müssten vorher geprüft werden.

PostgreSQL/pgvector, Supabase, Qdrant oder LanceDB sind erst bei einer bewusst beschlossenen zentralen Mehrbenutzer-/Serverarchitektur zu vergleichen. KalkPilot verwendet heute kein PostgreSQL; die im Text genannte „wenn PostgreSQL ohnehin verwendet wird“-Voraussetzung trifft daher nicht zu. Ein Vektordienst allein erzeugt keine Embeddings und löst keine GAEB- oder Preissemantik.

## J/K: Kleine nächste Umsetzungsschritte für Cloud und Codespaces

| Schritt | Geplante Dateien/Arbeit | Abnahme |
| --- | --- | --- |
| 1. Cloud-Start vereinheitlichen | Entwicklungs-/Prüfskripte unter scripts/, Dokumentation und festgelegte Cloud-Python-Version; vorhandene requirements-dev.txt verwenden | Ein Startbefehl betreibt die statische App; eine Prüfung bestätigt Einstiegsseite, lokale Skripte und einen Parser-/Browser-Smoke-Test |
| 2. Codespaces vorbereiten | .devcontainer/devcontainer.json; Cloud-Installation der Testabhängigkeiten und Chromium; Port 8000 beschriften/weiterleiten, privat belassen; browserbasierte Anleitung | Frischer Codespace lässt sich ohne Installation auf dem Firmenrechner starten und testen |
| 3. Releaseprüfung verknüpfen | Vorhandene Browser-CI beibehalten; dokumentierten Test-/Veröffentlichungsweg für main ergänzen | Branch/PR-Prüfungen sichtbar; gesamte statische Website einschließlich js/ und vendor/ erreichbar |
| 4. Datenmodell/Freigaben | Versionierte Metadaten, Migration und Review-Protokoll | Alte Sicherungen laden; unbekannte Felder sind sichtbar; Prüfstatus ist an konkrete Version gebunden |
| 5. Mehrstufiges Matching | Retrieval/Fachprüfung/Preisprüfung mit nachvollziehbarem Protokoll; Suchvergleich | Fachlich bewertete positive und negative Fälle; keine automatische Übernahme bei gesperrten/ungeklärten Kandidaten |
| 6. Kalkulationspilot | Vollständige Referenzansätze und geprüfte iTWO-Regeln für eine Leistungsfamilie | Rechenwerte und Export/Reimport stimmen mit bestätigten Beispielen überein; BETA bleibt sichtbar |

Schritte 1 und 2 sind mit Start-/Setup-/Prüfskripten, Anleitung und Devcontainer-Konfiguration vorbereitet. Der vorhandene Cloud-Rechner wird damit getestet; ein neu erstellter Codespace ist noch eine gesonderte Abnahme. Die Datenmodell- und Matching-Schritte bleiben geplante Folgearbeiten.

Ein npm-/Docker-Start ist nicht zwingend: Für die statische App reicht der vorhandene Python-Webserver **in der Cloud**. Die Bedienung auf dem Firmenrechner bleibt ausschließlich im Browser. Eine .env.example mit erfundenen Pflichtvariablen oder API-Schlüsseln bringt derzeit keinen Nutzen; erforderlich werdende nicht geheime Cloud-Variablen werden erst mit dem zugehörigen Feature dokumentiert.

Codex Cloud bzw. Claude Code Web bearbeiten denselben GitHub-Stand auf einem Branch. Codespaces ist eine zusätzliche mögliche Cloud-Ausführungsumgebung; benötigte Produktfreigaben und Firmenzugriff sind dort getrennt zu prüfen. Es werden keine Testdaten oder Arbeitsstände nur in einem Desktop-Verzeichnis als maßgebliche Quelle vorausgesetzt.

## L/M: Deployment und Betriebsgrenzen

Am Prüftag liefert die GitHub-Pages-API `source.branch=main`, `source.path=/`, `build_type=legacy` und `status=built`. Die bestehende Website ist https://kalkprofijanek.github.io/kalkpilot-by-janek/. Dies bestätigt den Veröffentlichungsweg, nicht die Auslieferung der noch offenen PR-Änderungen.

Den statischen Pages-Weg beibehalten. Nach Review und Merge prüfen, dass alle relativen Skripte und Lizenzen aus der neuen Version veröffentlicht wurden und der Firmenbrowser die Seite öffnen kann. Vercel/Railway/Render/Fly.io/Azure/Cloudflare sind derzeit kein erforderlicher Wechsel. Ein Pages-Deployment kann keinen geheimen serverseitigen API-Schlüssel schützen.

Aktuelle Betriebsregeln: keine produktiven LLM-Aufrufe, keine API-Schlüssel, keine Originalkundendaten in Git oder öffentlich zugänglichen CI-Artefakten; manuelle Uploads liegen beim Nutzer. IndexedDB gehört zum Profil und Website-Ursprung. Codespaces-Vorschau und Produktionsseite haben unterschiedliche Ursprünge und teilen deshalb keinen Referenzspeicher; der Umzug erfolgt per JSON-Sicherung. Der Entwicklungsport bleibt privat, damit ein Codespace keine versehentlich öffentliche Arbeitsoberfläche erzeugt.

Falls später produktive KI-APIs oder zentrale Teamdaten ausdrücklich gewünscht sind, benötigt dies eine getrennte Entscheidung: authentifizierter Backenddienst, serverseitige Secrets, Rollen/Zugriffsrechte, Aufbewahrungsregeln, begrenzte Logs und freigegebene Datendestinationen. Ein ChatGPT-/Claude-Abonnement ist weiterhin kein API-Zugang. Dieser optionale Ausbau ist nicht Bestandteil des vereinbarten Upload-Workflows.
