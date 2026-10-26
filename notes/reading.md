# Reading notes: the legal basis of lb-lint

Pre-M1 reading from PLAN.md. The statute text is copied verbatim (as of 2026-10-26). The observations at the end are open questions for the rule design, **not decisions**.

---

## 1. § 31 VgV — Leistungsbeschreibung

Source: <https://www.gesetze-im-internet.de/vgv_2016/__31.html> (official)

Scope: the VgV applies **above the EU thresholds**.

> (1) Der öffentliche Auftraggeber fasst die Leistungsbeschreibung (§ 121 des Gesetzes gegen Wettbewerbsbeschränkungen) in einer Weise, dass sie allen Unternehmen den gleichen Zugang zum Vergabeverfahren gewährt und die Öffnung des nationalen Beschaffungsmarkts für den Wettbewerb nicht in ungerechtfertigter Weise behindert.
>
> (2) In der Leistungsbeschreibung sind die Merkmale des Auftragsgegenstands zu beschreiben:
> 1. in Form von Leistungs- oder Funktionsanforderungen oder einer Beschreibung der zu lösenden Aufgabe, die so genau wie möglich zu fassen sind, dass sie ein klares Bild vom Auftragsgegenstand vermitteln und hinreichend vergleichbare Angebote erwarten lassen, die dem öffentlichen Auftraggeber die Erteilung des Zuschlags ermöglichen,
> 2. unter Bezugnahme auf die in Anlage 1 definierten technischen Anforderungen in der Rangfolge:
>    a) nationale Normen, mit denen europäische Normen umgesetzt werden,
>    b) Europäische Technische Bewertungen,
>    c) gemeinsame technische Spezifikationen,
>    d) internationale Normen und andere technische Bezugssysteme, die von den europäischen Normungsgremien erarbeitet wurden oder,
>    e) falls solche Normen und Spezifikationen fehlen, nationale Normen, nationale technische Zulassungen oder nationale technische Spezifikationen für die Planung, Berechnung und Ausführung von Bauwerken und den Einsatz von Produkten oder
> 3. als Kombination von den Nummern 1 und 2
>    a) in Form von Leistungs- oder Funktionsanforderungen unter Bezugnahme auf die technischen Anforderungen gemäß Nummer 2 als Mittel zur Vermutung der Konformität mit diesen Leistungs- und Funktionsanforderungen oder
>    b) mit Bezugnahme auf die technischen Anforderungen gemäß Nummer 2 hinsichtlich bestimmter Merkmale und mit Bezugnahme auf die Leistungs- und Funktionsanforderungen gemäß Nummer 1 hinsichtlich anderer Merkmale.
>
> Jede Bezugnahme auf eine Anforderung nach Nummer 2 Buchstabe a bis e ist mit dem Zusatz „oder gleichwertig" zu versehen.
>
> (3) Die Merkmale können auch Aspekte der Qualität und der Innovation sowie soziale und umweltbezogene Aspekte betreffen. Sie können sich auch auf den Prozess oder die Methode zur Herstellung oder Erbringung der Leistung oder auf ein anderes Stadium im Lebenszyklus des Auftragsgegenstands einschließlich der Produktions- und Lieferkette beziehen, auch wenn derartige Faktoren keine materiellen Bestandteile der Leistung sind, sofern diese Merkmale in Verbindung mit dem Auftragsgegenstand stehen und zu dessen Wert und Beschaffungszielen verhältnismäßig sind.
>
> (4) In der Leistungsbeschreibung kann ferner festgelegt werden, ob Rechte des geistigen Eigentums übertragen oder dem öffentlichen Auftraggeber daran Nutzungsrechte eingeräumt werden müssen.
>
> (5) Werden verpflichtende Zugänglichkeitserfordernisse im Sinne des § 121 Absatz 2 des Gesetzes gegen Wettbewerbsbeschränkungen mit einem Rechtsakt der Europäischen Union erlassen, so muss die Leistungsbeschreibung, soweit die Kriterien der Zugänglichkeit für Menschen mit Behinderungen oder der Konzeption für alle Nutzer betroffen sind, darauf Bezug nehmen.
>
> **(6) In der Leistungsbeschreibung darf nicht auf eine bestimmte Produktion oder Herkunft oder ein besonderes Verfahren, das die Erzeugnisse oder Dienstleistungen eines bestimmten Unternehmens kennzeichnet, oder auf gewerbliche Schutzrechte, Typen oder einen bestimmten Ursprung verwiesen werden, wenn dadurch bestimmte Unternehmen oder bestimmte Produkte begünstigt oder ausgeschlossen werden, es sei denn, dieser Verweis ist durch den Auftragsgegenstand gerechtfertigt. Solche Verweise sind ausnahmsweise zulässig, wenn der Auftragsgegenstand anderenfalls nicht hinreichend genau und allgemein verständlich beschrieben werden kann; diese Verweise sind mit dem Zusatz „oder gleichwertig" zu versehen.**

## 2. § 121 GWB — Leistungsbeschreibung

Source: <https://www.gesetze-im-internet.de/gwb/__121.html> (official)

> **(1) In der Leistungsbeschreibung ist der Auftragsgegenstand so eindeutig wie möglich zu beschreiben, sodass die Beschreibung für alle Unternehmen im gleichen Sinne verständlich ist und die Angebote miteinander verglichen werden können.** Die Leistungsbeschreibung enthält die Funktions- oder Leistungsanforderungen oder eine Beschreibung der zu lösenden Aufgabe, deren Kenntnis für die Erstellung des Angebots erforderlich ist, sowie die Umstände und Bedingungen der Leistungserbringung.
>
> (2) Bei der Beschaffung von Leistungen, die zur Nutzung durch natürliche Personen vorgesehen sind, sind bei der Erstellung der Leistungsbeschreibung außer in ordnungsgemäß begründeten Fällen die Zugänglichkeitskriterien für Menschen mit Behinderungen oder die Konzeption für alle Nutzer zu berücksichtigen.
>
> (3) Die Leistungsbeschreibung ist den Vergabeunterlagen beizufügen.

Footnote on the official page: *(+++ § 121: Zur Anwendung vgl. § 41 Abs. 2 MessbG +++)*

## 3. UVgO §§ 22–23 — below the EU thresholds

Source: <https://lxgesetze.de/uvgo/23> (a **secondary** source; the official publication is in the Bundesanzeiger, version of 2 Feb 2017, last amended 8 Feb 2017).

The UVgO is not a statute. It is a procedural code that becomes binding through federal or Land budget rules (Haushaltsrecht). Most municipal procurement falls under it.

**§ 22 Aufteilung nach Losen** covers splitting a contract into lots (Teillose / Fachlose). It doesn't deal with the wording of the Leistungsbeschreibung, so it matters little for lb-lint.

**§ 23 Leistungsbeschreibung:**

> **(1) In der Leistungsbeschreibung ist der Auftragsgegenstand so eindeutig und erschöpfend wie möglich zu beschreiben, sodass die Beschreibung für alle Unternehmen im gleichen Sinne verständlich ist und die Angebote miteinander verglichen werden können.** Die Leistungsbeschreibung enthält die Funktions- oder Leistungsanforderungen oder eine Beschreibung der zu lösenden Aufgabe, deren Kenntnis für die Erstellung des Angebots erforderlich ist, sowie Umstände und Bedingungen der Leistungserbringung.
>
> (2) Die Leistungsbeschreibung kann auch Aspekte der Qualität sowie soziale, innovative und umweltbezogene Merkmale umfassen. Diese können sich auch auf den Prozess oder die Methode zur Herstellung oder Erbringung der Leistung oder auf ein anderes Stadium im Lebenszyklus des Auftragsgegenstands einschließlich der Produktions- und Lieferkette beziehen, auch wenn derartige Faktoren keine materiellen Bestandteile der Leistung sind, sofern diese Merkmale in Verbindung mit dem Auftragsgegenstand stehen und zu dessen Wert und Beschaffungszielen verhältnismäßig sind.
>
> (3) In der Leistungsbeschreibung kann ferner festgelegt werden, ob Rechte des geistigen Eigentums übertragen oder dem Auftraggeber daran Nutzungsrechte eingeräumt werden müssen.
>
> (4) Bei der Beschaffung von Leistungen, die zur Nutzung durch natürliche Personen vorgesehen sind, sind bei der Erstellung der Leistungsbeschreibung außer in ordnungsgemäß begründeten Fällen die Zugänglichkeitskriterien für Menschen mit Behinderungen oder die Konzeption für alle Nutzer zu berücksichtigen.
>
> **(5) Bezeichnungen für bestimmte Erzeugnisse oder Verfahren wie beispielsweise Markennamen dürfen ausnahmsweise, jedoch nur mit dem Zusatz „oder gleichwertig", verwendet werden, wenn eine hinreichend genaue Beschreibung durch verkehrsübliche Bezeichnungen nicht möglich ist. Der Zusatz „oder gleichwertig" kann entfallen, wenn ein sachlicher Grund die Produktvorgabe ansonsten rechtfertigt. Ein solcher Grund liegt insbesondere dann vor, wenn die Auftraggeber Erzeugnisse oder Verfahren mit unterschiedlichen Merkmalen zu bereits bei ihnen vorhandenen Erzeugnissen oder Verfahren beschaffen müssten und dies mit unverhältnismäßig hohem finanziellen Aufwand oder unverhältnismäßigen Schwierigkeiten bei Integration, Gebrauch, Betrieb oder Wartung verbunden wäre. Die Gründe sind zu dokumentieren.**

## 4. eForms and the Bekanntmachungsservice

- **eForms** is the EU's structured format for procurement notices. It has been mandatory for EU-wide notices since 25 Oct 2023, and Germany uses the national profile **eForms-DE**. ([Vergabeblog](https://vergabeblog.de/2023-10-09/eforms-und-der-steinige-weg-der-umsetzung-nicht-nur-in-deutschland/))
- **Data flow:** notices go to a central Vermittlungsdienst, which validates them. **Above-threshold** notices are forwarded via the eSender-Hub to **TED**. **Below-threshold** notices go to the **Bekanntmachungsservice** (`oeffentlichevergabe.de`) **only, not to TED**. The Bekanntmachungsservice is a central portal for federal, Land and municipal notices and offers an open-data interface. ([Bremen press release](https://www.finanzen.bremen.de/sixcms/media.php/13/231027_Pressemitteilung_eForms_D%C3%96E-v04.pdf), [cosinex](https://blog.cosinex.de/2023/10/27/start-des-datenservice-oeffentlicher-einkauf/))
- **CPV** (Common Procurement Vocabulary) is the EU's hierarchical code list for what is being bought, e.g. `30213100` portable computers. The first two digits are the division (30 = office and computing machinery, 48 = software packages). Every notice carries at least one CPV code, which makes it the natural label for the clustering in M3.
- I couldn't find documentation of the open-data API itself (endpoints, formats). If M3 needs it, look it up directly before starting.

---

## 5. What this means for lb-lint (open questions, not decisions)

1. **PLAN.md misattributes a phrase.** It says § 121 Abs. 1 GWB requires "eindeutig und erschöpfend". The GWB only says *"so eindeutig wie möglich"*. *"Erschöpfend"* comes from **§ 23 Abs. 1 UVgO** (and older VOL/A wording). The vagueness rule's `rechtsgrundlage` should cite what the text actually says.

2. **"oder gleichwertig" is necessary but not sufficient under § 31(6) VgV.** A product reference is only allowed if (a) the subject matter justifies it, or it can't otherwise be described precisely, **and** (b) it carries the addition. The planned rule ("flag unless *oder gleichwertig* is in the same sentence") treats (b) as sufficient. A deterministic rule can check (b) but not (a). Should a reference that *has* "oder gleichwertig" still produce a lower-severity hint ("Begründung prüfen")?

3. **The statute says "oder gleichwertig", not "oder vergleichbar".** PLAN.md accepts both. Is "oder vergleichbar" good enough, or is that itself a finding?

4. **The scope is wider than brand names.** § 31(6) covers *Produktion, Herkunft, besonderes Verfahren, gewerbliche Schutzrechte, Typen, Ursprung*. A brand gazetteer catches brands and some types (e.g. "ThinkPad", "Intel Core i7"). It misses origin ("aus deutscher Fertigung") and process references. Is that an accepted, documented gap for M1?

5. **§ 31(2) VgV is a second, easy "oder gleichwertig" rule.** Every reference to a norm (DIN, EN, ISO, …) also needs *"oder gleichwertig"*. That is regex-detectable and has a clean legal basis. Is it worth adding as a rule?

6. **The two regimes give different verdicts.** Below the threshold (§ 23(5) UVgO), "oder gleichwertig" **may be dropped** if a documented sachlicher Grund exists, e.g. compatibility with existing equipment. Above it (§ 31(6) VgV), the addition is always required. The same sentence can therefore be a violation in one regime and fine in the other. Does lb-lint need a `regime: VgV | UVgO` input, and does every `rechtsgrundlage` depend on it?

7. **The corpus is biased.** TED only receives above-threshold notices. A TED-only corpus (M3) contains no UVgO procurements, which are the most common municipal case. Is that acceptable, or should the Bekanntmachungsservice be the source?
