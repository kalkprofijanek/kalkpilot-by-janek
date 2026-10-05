# Referenz- und Preisprüfung · BETA

Historische Referenzen können fachlich passen, obwohl ihre Preisbasis unvollständig ist. Die App bezeichnet gespeicherte Werte deshalb als **ungeprüfte Ansatzsummen**, auch in CSV-Ausgaben. Eine manuelle oder automatische Referenzübernahme ist keine Preisfreigabe.

Die Prüfung zeigt offene Geräte-/Kalkulationsbausteine, fehlende oder ungültige Ansatzwerte, Nullpreise bei Mengenansätzen, abweichende Faktoren, deaktivierte Kostenzeilen und Pauschalierungen (`sItemLSum` / `sItemLSumAbs` in Subitems). Diese Auffälligkeiten verhindern eine automatische Referenzübernahme. Manuelle Übernahme und Original-XML-Export bleiben möglich; die ursprünglichen Preise und Kalkulationsdaten werden nicht verändert.

Im Positionsdetail erscheint ein Vergleich aktiver Referenzen mit gleichem normalisiertem Kurz- oder Langtext und gleicher Einheit. Stunden-Einheiten wie h und Std werden zusammengeführt. Kurze Sammeltexte und fehlende Einheiten reichen nicht aus. Die Anzeige enthält die ausgewählte Referenz und höchstens neun weitere Kandidaten, getrennte XML-/LV-Mengen, Text, Kostenzeilen und Prüfhinweise. Sie erzeugt weder einen Durchschnittspreis noch ein fachliches Gleichheitsurteil. Ein gleichlautender Standardtext kann unterschiedliche Leistungen begleiten.

Die App rekonstruiert noch keinen geprüften vollständigen Einheitspreis aus Leistungsfaktoren, Pauschalen, Gerätebausteinen und Zuschlägen. Dazu müssen die Rechenregeln des Ursprungssystems und dessen Kontrollwerte nachvollzogen werden. Faktoren dürfen nicht pauschal multipliziert oder dividiert werden. Ein Nullpreis kann eine beigestellte oder anderweitig enthaltene Leistung bezeichnen; er wird nicht automatisch als Fehler korrigiert.

Browser-Regressionen prüfen, dass Faktoren, Nullpreise und Pauschalansätze automatische Übernahmen blockieren, Vergleichskandidaten gleiche Einheiten besitzen, HTML in Referenzdaten nicht ausgeführt wird und Preise unverändert bleiben. Kundendaten gehören nicht ins Repository.

## Teilkostenberechnung ab Version 1.3.0 BETA

Für jede Kostenzeile unterscheidet die App **berechnet**, **offen** und **ausgeschlossen**. Menge × Preis wird nur berechnet, wenn beide Werte gültig sind, der Preis nicht null ist, kein Leistungsfaktor gesetzt ist, sämtliche vorhandenen Faktoren 1 sind und keine andere Währung als EUR angegeben ist. Negative Beträge bleiben als negative Ansätze erhalten. Deaktivierte Zeilen und Mengenansätze 0 werden ausgeschlossen. Bausteine ohne Preis und andere Nullpreise bleiben offen; sie werden nicht als kostenlose Leistung eingerechnet.

Die Summe ist ausschließlich die Summe der berechenbaren Kostenzeilen. Ein leerer bekannter Anteil erscheint nicht als 0 €. Nicht auflösbare Bausteine können dauerhaft offen bleiben. Die App ergänzt dafür keine erfundenen Gerätepreise. Bei Pauschalierungen, abweichenden Subitem-Faktoren/-Mengen oder unklarer Bezugsmenge wird keine Umrechnung in einen LV-Einheitspreis vorgenommen.

Auch wenn alle Ansatzkosten eindeutig berechenbar sind, sind Preisstand, Zuschläge und Angebotspreis nicht freigegeben. Die Berechnung verändert weder gespeicherte historische EP-Werte noch Kostenansätze oder Original-XML. CSV-Ausgaben und KI-Prüfpakete enthalten die Teilkosten samt offenen Anteilen bzw. Mengenbasis-Hinweisen.
