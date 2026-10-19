# 06 | Compliance and submission checklist

**Priority: registration deadline 25 October 2026.** Source hierarchy: 2027 FaceVitals official document for the task; uploaded September 2026 SPS Student Competition Terms & Conditions v1.4 for eligibility/judging/travel; ask organizers when versions disagree.

## Team formation (from uploaded September 2026 Terms & Conditions)

- [ ] One eligible **faculty** supervisor (the document excludes postdocs and research associates as faculty).
- [ ] **3–10 undergraduate** team members (the document defines undergraduate as not having earned a 4-year degree).
- [ ] At least **three undergraduate SPS student members**, membership active at registration and maintained until competition end.
- [ ] At most **one graduate tutor** (optional); tutor not eligible for prizes/travel grant.
- [ ] No participant belongs to more than one team/competition simultaneously.
- [ ] Check prior SPS finalist/top-three eligibility and travel-support restrictions.
- [ ] Verify that no team members will need to change after registration deadline.
- [ ] Supervisor completes IEEE conflict-of-interest form before participation.
- [ ] Each team member reads and agrees to the terms; submit signed form per official site.
- [ ] At least **one undergraduate** can attend the ICASSP finals **in person**, subject to the organizer's published visa/exception process.
- [ ] Complete [official registration](https://www2.securecms.com/SPCup/SPCRegistration.asp) by **25 October 2026**.

## Milestones (FaceVitals official challenge, accessed 19 October 2026)

| Item | Date |
|---|---|
| Registration | 25 October 2026 |
| Round 1 | 30 November 2026 |
| Round 1 results | 5 December 2026 |
| Round 2 | 16 January 2027 |
| Round 2 results | 21 January 2027 |
| Three finalist teams announced | 9 February 2027 |
| ICASSP 2027 | 16–21 May 2027 |

## Round-1 technical checklist

- [ ] Real RGB facial videos under controlled and uncontrolled conditions.
- [ ] Real synchronized HR reference from clinical pulse oximeter or ECG (not synthetic HR labels).
- [ ] GREEN, POS, CHROM reproducible baselines with shared preprocessing.
- [ ] Face detection, landmark ROI masks, timestamp handling and multi-video repeatability.
- [ ] **At least two constraints C1–C7** explicitly tested/addressed; explain limitations.
- [ ] MAE, RMSE, Pearson r and Bland–Altman statistics, with sample sizes and failure-case breakdown.
- [ ] Report in IEEE conference-paper format, with code and required data exports.
- [ ] Required reference videos/.mat/CSV folders and metadata according to clarified official specification.
- [ ] For any **team-collected human-subject data**, obtain institutional ethical/IRB approval and informed consent before collection, and document them as required by the challenge.

## Competition scoring (September 2026 PDF v1.4)

The uploaded terms list six equally weighted criteria, unless the official challenge document specifies otherwise: (1) innovation and thorough experiments, (2) validation-set performance, (3) test-set performance, (4) model/time complexity, (5) final report quality/clarity, (6) presentation quality/clarity. The general SPS web page currently lists a different five-criterion scheme; **obtain confirmation** of the governing rules for this competition.

## Ethics, files, and medical claims

- Do **not** collect identifiable human facial videos or vital-sign ground truth without the required consent and ethics approvals.
- Do **not** upload protected BP4D+/organizer datasets to public repositories without written permission.
- Do **not** call RGB-only SpO2 or BP estimates clinical measurements until properly validated.
- Do **not** report CSV results from the supplied synthetic trace generator as official or real-video scores.
- Retain experiment configuration, source licensing, subject-level splits, camera metadata and actual time/latency measurements.

## URLs

General SPS page: https://signalprocessingsociety.org/community-involvement/signal-processing-cup  
2027 FaceVitals technical document: https://signalprocessingsociety.org/sites/default/files/2026-10/2027-SP-Cup-Official-Document-FaceVitals.pdf  
SPS conflict of interest: https://www.ieee.org/about/compliance/conflict-of-interest/coiandpob.html  
Organizer: vijayjeyakumar@ieee.org (copy: sp-competitions@listserv.ieee.org)
