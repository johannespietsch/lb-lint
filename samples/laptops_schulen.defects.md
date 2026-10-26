# Planted defects in `laptops_schulen.md`

The key to the sample document. **This is not the golden-set annotation.** M2 annotates from the raw text, following `eval/ANNOTATION_GUIDELINES.md`.

| # | Section | Text | Kind | Expected rule behaviour | Notes |
|---|---|---|---|---|---|
| 1 | 2 | `Intel Core i5 der 13. Generation` | Type/brand reference without "oder gleichwertig" | LB1xx violation | The core § 31(6) case |
| 2 | 2 | `Das Display muss eine hohe Farbtreue aufweisen.` | No measurable unit | Missing-unit rule | `hohe` is not in the planned lexicon, so it needs the unit check |
| 3 | 2 | `ausreichende Akkulaufzeit für einen vollständigen Schultag` | Vague | LB2xx (`ausreichend`) | "Schultag" makes it look measurable, but it is not |
| 4 | 2 | `robust und für den Schulalltag geeignet` | Vague, no unit | LB2xx / missing unit | Not in the lexicon: tests recall beyond the word list |
| 5 | 3 | `DIN EN ISO 9241-307` without "oder gleichwertig" | Norm reference without the addition | **Only if** the § 31(2) rule is adopted (reading note, Q5) | |
| 6 | 3 | `aus europäischer Fertigung` | Origin reference | § 31(6) "Herkunft" — **not caught** by a brand gazetteer (Q4) | Recall gap, on purpose |
| 7 | 4 | `Microsoft Office 2024 Education` | Brand without "oder gleichwertig" | LB1xx violation | |
| 8 | 4 | `Lenovo ThinkPad Universal USB-C Dock oder vergleichbar` | "oder vergleichbar" instead of the statutory wording | Depends on Q3 | |
| 9 | 5 | `zeitnah auszutauschen` | Vague | LB2xx (`zeitnah`) | |
| 10 | 6 | `marktüblicher Verpackung` | Vague | LB2xx (`marktüblich`) | Low stakes, so a candidate for severity `hinweis` |

## Correct-looking cases (false-positive traps)

| Section | Text | Why it is there |
|---|---|---|
| 3 | `TCO Certified … oder gleichwertig` | A label reference that does carry the addition. Should not be flagged as a violation (Q2: a hint at most) |
| 4 | `Microsoft Windows 11 Pro Education oder gleichwertig` + stated criteria for equivalence | The textbook-correct form, with the addition and a definition of equivalence |
| 6 | `Back-Office Medienausstattung` | "Office" in an address: a gazetteer false positive the M4 critique should catch |
| 2 | `IEEE 802.11ax (Wi-Fi 6) oder neuer`, `HDMI 2.0`, `USB-C` | Interface standards, not brands. The gazetteer must not contain them |

## Segmentation traps (M1 trap)

`gemäß § 15 VgV`, `gemäß § 57 Abs. 1 VgV`, `ggf.`, `inkl.`, `z. B.`, `i. V. m.`, `cd/m²`, `1.200`, `13,3`

## Annotation questions this document raises (for M2 guidelines)

- **Interfaces bullet (section 2):** one bullet with four interface requirements. Is it one Anforderung or four?
- **Windows paragraph (section 4):** a requirement plus three equivalence criteria. Is that one Anforderung or four?
- **Section 1 (scope, 1,200 devices) and the procedural sentence in section 2:** are they Anforderungen at all?
