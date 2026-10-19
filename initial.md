photoplethysmography related existing algorithms, analysis on them which one is best. (find best/most suited solution and report back failure rates, where it shines most / constraints)


link = https://signalprocessingsociety.org/community-involvement/signal-processing-cup

IMPORTANT: All team members must fully read and agree to the terms in this SPS Student Competition Terms and Conditions document in order to be eligible in any SPS Student Competition. By checking the agreement checkbox during team registration, all team members agree to all of the Terms & Conditions mentioned in this document:

>> Download a copy of the full SPS Student Competition Terms & Conditions

IMPORTANT: [Judges and Team Supervisors] The IEEE Conflict of Interest form must be completed before participating in the competition. Complete the Conflict of Interest form.

Team Formation and Eligibility
Final Round Judging Criteria for SPS Competitions
Judge & Team Supervisor Participation and Conflict of Interest
Prizes for Finalists
 

Sponsorship of the SPS Signal Processing Cup
MathWorks

We gratefully acknowledge MathWorks, Inc. for their continued support of IEEE Signal Processing Cup. Participating students are encouraged to download the complimentary Mathworks Student Competitions Software for use in the competition.

 

IEEE SP Cup 2027
Past IEEE SP Cups
IEEE Signal Processing Cup at IEEE ICASSP 2027
FaceVitals: Contactless, Bias-Robust Estimation of Heart Rate, SpO₂, Blood Pressure, from RGB Facial Videos

IEEE ICASSP 2027 Website | 16-21 May 2027 | 2027 SP Cup Official Document

[Sponsored by the MathWorks and IEEE Signal Processing Society]

Introduction
This challenge encourages young innovators to develop practical, technology-driven solutions that improve healthcare accessibility. One exciting development in this space is camera-based vital sign monitoring, which allows a smartphone's ordinary front or rear camera to estimate physiological parameters such as heart rate, blood oxygen saturation, blood pressure, simply by observing subtle changes in a person's facial skin over a short video. This capability is especially valuable in settings where clinical infrastructure is limited or unavailable remote villages, ambulances, disaster-response zones, telehealth consultations, and everyday home monitoring for the elderly or chronically ill.

Traditionally, measuring vital signs has required dedicated contact-based hardware: a pulse oximeter clipped to a finger, a cuff wrapped around the arm, a thermometer pressed to the skin. Each device solves one problem in isolation, and each requires the patient to be physically present with the right equipment on hand. But the human face already carries this information. Blood flow driven by each heartbeat produces imperceptible, rhythmic changes in skin color and reflected light; this signal, invisible to the naked eye, can be recovered computationally from ordinary RGB video through the science of remote photoplethysmography (rPPG). In principle, a single smartphone camera pointed at a person's face for under a minute could recover the same vital signs a nurse would otherwise take five separate instruments to collect.

The central challenge is achieving this reliably outside the laboratory. Existing camera-based vital sign systems, including several already available commercially, perform well under favorable conditions: good lighting, high-resolution cameras, a single cooperative subject facing the camera directly. Real-world deployment is far less forgiving. Lighting is often dim or uneven, skin tones and conditions vary enormously across a population, cameras in low-cost or remote-area devices offer limited resolution and unstable bandwidth for streaming, subjects may be elderly with wrinkled or aged skin, may have visible skin conditions such as vitiligo, may be partially masked, or may simply be one face among several in the frame. A system that only works in ideal conditions is of little use to the populations who would benefit from it most.

This problem matters because most current camera-based vital sign solutions either depend on heavy cloud-based computation, are validated only on narrow, curated datasets, or have not been tested for fairness across skin tone, gender, and age. Robust, edge-deployable, clinically validated extraction of vital signs from ordinary RGB video without thermal or contact sensors remains an open and consequential engineering problem, with direct implications for equitable, low-cost, remote healthcare access.

For more clarity: participants are encouraged to watch the following concept and demonstration videos of existing camera-based vital sign monitoring technologies made available for public viewing:

[1]. FaceHeart Vitals™ demonstration — contactless vital sign measurement through a single camera lens: https://www.youtube.com/watch?v=S2u2fLW2fHI

[2]. Binah.ai — video-based vital sign monitoring using only a smartphone camera: https://www.youtube.com/shorts/GqcO0WK-hY8

[3]. Binah.ai (Bvue) — CES demonstration of camera-based health checks: https://www.youtube.com/watch?v=qDDGioLrNpU

Full technical details, dataset(s), evaluation metrics, and all other pertinent information about the competition is located in the "2027 SP Cup Official Document" (above).

 

Important Dates
Challenge Announcement/Registration Starts: 11 September 2026
Team Registration Deadline: 25 October 2026 - Registration Link
Phase 1 Team Work Submission Deadline: 30 November 2026
Phase 1 Results: 05 December 2026
Phase 2 Team Work Submission Deadline: 16 January 2027
Phase 2 Results: 21 January 2027
Announcement of 3 Finalists Teams: 09 February 2027
Final Competition at ICASSP 2027: 16-21 May 2027
 

Registration and Important Resources
 

Official SP Cup Team Registration
All teams MUST be registered through the official competition registration system before the deadline in order to be considered as a participating team. Teams must meet all eligibility requirements at the time of team registration as well as throughout the competition.
All team members for each team MUST agree to the SPS Student Terms and Conditions and submit a completed agreement form here before the team registration deadline.
Register your team for the 2027 SP Cup before the Team Registration Deadline date above and submit work for each phase by the respective submission due date above at the following link: [Register your team HERE]
 

Complimentary MATLAB License
MathWorks, Inc. continues to support the IEEE SP Cup. Participating students are encouraged to download the complimentary MathWorks Student Competitions Software for use in the competition

Instructions on how to apply for the complimentary MATLAB License can be found in the following DropBox folder

DropBox Folder: SP Cup - Complimentary MATLAB License (MathWorks)

 

Contacts
Competition Organizers (technical, competition-specific inquiries): Dr. Vijay Jeyakumar, IEEE SPS Madras Chapter - Secretary

SPS Staff (Terms & Conditions, Travel Grants, Prizes): Jaqueline Rash, SPS Membership Program and Events Manager

SPS Student Services Committee: Lucas Thomaz, Chair

Questions and general inquiries regarding the competition should be sent to sp-competitions@listserv.ieee.org.

 

Sponsors
This competition is sponsored by the IEEE Signal Processing Society and MathWorks:

//

what we should do, First research on the algorithms run some simulations make csv reports to analyse and then find the constraints, reportings, If possible think something genuine in the field. First guide me through the algorithms their processes how do they work in the background.


# Useful link I found after own research

https://cameravitals.github.io/

https://www.cs.binghamton.edu/~lijun/Research/3DFE/3DFE_Analysis.html

these two links have the emails to the Dataset, we need to email the professors to request and get the dataset.

# Preferred output format :

Possibly md files, pdf of explanations with visual diagrams of how each algorithms work, python files.