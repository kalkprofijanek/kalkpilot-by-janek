# Referenz- und Preisprüfung · 1.5.0 BETA

**Kostenarten und Gerätebausteine beziehen ihre Preise beim i2-Import aus Stammdaten.** Ein leerer oder mit null exportierter Preis ist ein regulärer Verweis, kein fehlendes Gerät und kein automatisch fehlerhafter Kalkulationsansatz. Entscheidend sind korrekte Kennungen sowie Mengen-, Kosten- und Leistungsfaktoren.

Ein Gerätebaustein kann Baggermiete, Diesel, Bedienpersonal und GPS umfassen. Die vorhandenen XML-Verweise nennen Gerät, Kennung, Menge und Faktoren; sie enthalten nicht zwingend die Einzelbestandteile. KalkPilot erhält die Verweise. Es ergänzt keine vermuteten Komponenten und rechnet Bedienpersonal oder Diesel nicht zusätzlich hinein. Der tatsächliche Abgleich der Kennungen mit dem firmeneigenen Stammdatenkatalog erfolgt in i2.

## Fachliche Zuordnung und Kalkulationsstruktur

Die Fachprüfung bewertet Leistungsumfang, Abmessungen, Material und Ausführungsverfahren. Fehlende Kostenarten-/Gerätekennungen, ungültige Mengen oder ungültige Faktoren werden als Strukturhinweise angezeigt. Ein Faktor null wird nicht mehr stillschweigend in 1 umgewandelt. Gültige Leistungsfaktoren und Stammdatenpreise blockieren eine fachlich passende Referenz nicht allein wegen einer unvollständigen Browser-Preisanzeige.

KI-Zuordnungen beginnen weiterhin unbestätigt. Eine Referenzübernahme bestätigt keinen Angebotspreis. Original-XML bzw. rekonstruierte Geräteverweise erhalten Mengen, Kennungen, Leistungsfaktor-Flags und Kostenfaktoren. KalkPilot erfindet keine Rechenregel für die Leistungsansätze und keine aktuellen Stammdatenpreise.

## Anzeige der Exportwerte

Kostenzeilen erscheinen getrennt als **einfacher historischer Betrag**, **i2-Stammdatenverweis**, **in i2 zu berechnender Leistungs-/Faktoransatz**, **ungültiger Wert** oder **ausgeschlossen**. Nur gültige einfache Menge-mal-Preis-Zeilen ohne abweichende Faktoren werden als bekannter historischer Anteil addiert. Zeilen mit null oder leerem Preis erscheinen nicht als kostenlose Leistung. Deaktivierte Zeilen und Mengenansätze null werden ausgeschlossen. Negative einfache Beträge bleiben negativ.

Ein Leistungsfaktor wird nicht pauschal als Multiplikator verwendet. Pauschalierung, Subitem-Mengen und Faktoren können die Bezugsbasis verändern. Daher wird aus unklaren Ansätzen kein €/LV-Einheit-Wert errechnet. Die vollständige Berechnung erfolgt in i2.

## Absolute Preisvergleiche

Im Positionsdetail lassen sich aktive Referenzen mit gleichen normalisierten Texten und Einheiten vergleichen. Die Kandidatenliste kann gleiche Kurz- oder Langtexte enthalten; das beweist noch keine gleiche Leistung. Eine absolute Betragsdifferenz wird nur für identische Kurz- **und** Langtexte, gleiche Einheiten, eindeutige Mengenbasis und vollständig einfach berechenbare positive historische Ansätze gezeigt. Stammdatenverweise, Leistungsfaktoren, Pauschalansätze oder unterschiedliche Texte bleiben ohne rechnerischen Preisvergleich.

Zusätzlich zur Differenz pro Einheit kann die App die rechnerische Mengenwirkung für das neue LV zeigen. Beispiel: 0,70 gegenüber 1,50 €/m³ bedeutet +0,80 €/m³; bei 20.000 m³ ergibt sich +16.000 €. Das ist eine Vergleichsrechnung historischer Ansätze, kein neuer Angebotspreis. Preisstand, Region, Zuschläge und Leistungsumfang müssen bestätigt werden. Preise beeinflussen die fachliche Rangfolge nicht; es gibt keine pauschale Prozent- oder Eurogrenze und keine vorgetäuschte statistische Toleranz.

## Rückmeldungen

Im Matching-Detail kann Feedback mit Grund gespeichert werden. Falscher Leistungsumfang, falsches Material/Maße und falsches Verfahren gehen als fachliche Ablehnung in das Matching-Wissen ein. Hinweise zu Kostenart/Gerät, Leistungsansatz oder Preisstand werden getrennt gesammelt und verschlechtern keine fachliche Zuordnung. Der Download enthält Texte und Ressourcen-/Faktorkontext zur späteren Prüfung. Benutzerhinweise sind keine unabhängig bestätigten Musterlösungen.

[Größerer Originaldaten-Prüflauf und Copilot-Prüfpakete](MATCHING_ORIGINALDATEN.md).
