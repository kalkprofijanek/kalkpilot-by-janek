# Vertiefte Matching-Prüfung

Der Ausbau verbessert die gemeinsame Fachprüfung von Regelvergleich und KI-Import sowie die Kandidatensuche und die Sammelübernahme. Die Änderungen sind lokal im Projekt umgesetzt; eine Veröffentlichung erfolgt erst über den bestehenden Pages-Workflow.

## Fachliche Änderungen

| Situation | Verhalten |
| --- | --- |
| Rohr da 75 mm gegenüber da 0,075 m oder 7,5 cm | Außendurchmesser werden in Millimeter vereinheitlicht. DN bleibt eine eigene Größe. |
| Rohr da 75 cm gegenüber da 75 mm | Fachwiderspruch trotz gleicher Ziffern. |
| Rohrwerkstoff PE gegenüber PVC, PP gegenüber PVC oder Stahl gegenüber Beton | Erkannte unterschiedliche Werkstofffamilien erzeugen einen Fachwiderspruch. Fehlender Zielwerkstoff in der Referenz bleibt offen. |
| Rohr mit PP-Bettungsvlies | Ein beiläufig genanntes PP wird nicht als Rohrwerkstoff übernommen. Erkannt werden Rohrbezeichnungen, explizite Werkstoffangaben und PE-Klassen. |
| Entsorgung ist nicht enthalten / Lieferung wird gesondert vergütet | Nachgestellte Ausschlüsse werden berücksichtigt. |
| Rohr ohne Lieferung verlegen | Der Ausschluss der Lieferung verneint nicht zugleich das Verlegen. „Nicht nur liefern, sondern …“ wird nicht als Lieferausschluss interpretiert. |
| Transportweg 1.000 m gegenüber 1 km | Gleichwertige Zahlenangabe im deutschen Zahlenformat; auch 1.500,5 m und 1,5005 km werden vereinheitlicht. |
| Unterschiedliche eindeutige Transportentfernungen | Fachwiderspruch. Fehlende Entfernungen, mehrere Werte, Bereiche und Näherungen bleiben offen. |
| Abrechnung in kg gegenüber t oder fehlende Einheit | Die Bezugsbasis bleibt zur Prüfung offen; Ansätze werden nicht automatisch umgerechnet. |

## Kandidaten und Übernahme

Vor dem Kürzen der Kandidatenlisten fließt die gemeinsame Fachprüfung in die schnelle Suchrangfolge ein: Widersprüche senken den Suchwert um zwölf, fehlende Angaben um zwei heuristische Punkte. Das betrifft die automatische Vorauswahl, das Nachsuchen über den gesamten Bestand und die Vorschlagsliste der manuellen Suche. Anschließend führt `calcScore` weiterhin die ausführliche Prüfung durch. Suchpunkte sind keine Wahrscheinlichkeit. Die begrenzten Suchfenster bleiben bestehen; eine vollständige Suche nach jedem möglichen Treffer wird dadurch nicht garantiert.

Das Nachsuchen respektiert jetzt den aktivierten Filter auf gleiche Einheit. Zuvor konnte dieser Weg Referenzen mit abweichender Einheit wieder in die Kandidatenliste aufnehmen.

Die Sammelübernahme ab einer Punkteschwelle verwendet jetzt dieselbe Übernahmeprüfung wie das automatische Matching. Fachwidersprüche, offene Fachangaben, Strukturmängel, knappe Alternativen und ungeprüfte KI-Vorschläge bleiben zur Einzelprüfung offen. Bereits ausdrücklich übernommene Positionen bleiben erhalten. Vor der automatischen Übernahme werden die aktuellen Texte erneut fachlich geprüft, auch wenn alte Debug-Daten einen hohen Score enthalten. Der Prüfpfad unterscheidet Widersprüche von unvollständigen Angaben und nennt die aktuellen Gründe. Eine Referenzübernahme ist weiterhin keine Preisfreigabe.

## Prüfung und Grenzen

Der erste vertiefte Ausbau erweiterte die synthetische Fachfall-Datei von 69 auf 99 Fälle, darunter gültige Gegenbeispiele zu den neuen Ausschlüssen. Der anschließende [Praxistest mit öffentlichen LVs](OEFFENTLICHE_LV_PRUEFUNG.md) erweitert sie auf 123 Fälle. Die Browser-Tests prüfen zusätzlich die vollständigen Abläufe:

- Eine gültige Rohrreferenz hinter 260 gleich benannten, aber fachlich widersprüchlichen Referenzen bleibt im automatischen und manuellen Vorschlagsweg auffindbar.
- Der Einheitenfilter bleibt beim Nachsuchen wirksam.
- Die Sammelübernahme lässt nachträglich veränderte Rohrmaße, ungeprüfte KI-Vorschläge und knappe Alternativen offen.
- Eine KI-Antwort mit hoher Sicherheit und echten, aber unzureichenden Textbelegen verdeckt keinen Rohrwerkstoffwiderspruch.

Die Merkmalsextraktion bleibt eine Textmusterprüfung. Nicht erfasste Schreibweisen, komplexe Leistungsabgrenzungen, Werkstoffunterklassen und projektbezogene Sonderregeln benötigen fachliche Prüfung. Ein bestandener synthetischer Fall ist keine unabhängig bestätigte Trefferquote auf Kunden-LVs. Der anschließende Praxistest prüft zwei öffentliche Original-LVs; externe KI-Dienste wurden dabei nicht aufgerufen.

Reproduzieren im Cloud-Terminal:

```sh
bash scripts/test-cloud.sh
python3 scripts/matching_quality_cloud.py \
  --baseline-ref HEAD \
  --output-dir /workspace/analysis/matching-deep
```

`HEAD` bezeichnet den zum Ausführungszeitpunkt lokal eingecheckten Stand. Der Vergleich umfasst die gemeinsame Merkmalsprüfung auf denselben synthetischen Fällen; die zusätzlichen Browser-Tests sichern Kandidatensuche und Übernahme ab.
