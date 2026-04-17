# PHISGUARD FYP Report Skeleton (Mapped to Template)

## Cover Page
- Project title: PHISGUARD: A Web-Based Phishing Simulation and Awareness Platform
- URL to prototype/code: (GitHub repo link)
- Student name and banner ID
- Supervisor name
- Word count
- Programme title

## Abstract (250-500 words)
- Problem: phishing remains effective due to human factors.
- Solution: PHISGUARD web platform with realistic email/SMS simulations.
- Implementation: Flask backend, React frontend, role-based login, feedback and metrics.
- Findings: summary of testing outcomes and user performance trends.
- Conclusion: project value, limitations, and future work.

## Declaration of AI Use
- Complete YES/NO fields from your template.
- Add brief note of AI use for outline/language support only if applicable.

## Acknowledgements
- Supervisor, peers, testers, and any support sources.

## 1. Introduction
### 1.1 Background
- Why phishing is still a major issue.
- Why simulation-based training is relevant.
- Target users: students/staff in controlled training environment.

### 1.2 Aims and Objectives
- Aim: design, build, and evaluate PHISGUARD.
- Objectives:
- Build phishing + legitimate email/SMS scenarios.
- Implement interaction flow (click/report) with immediate feedback.
- Add admin controls and metrics.
- Evaluate usability and effectiveness.

### 1.3 Methodology
- Iterative prototyping and testing.
- Scenario design based on literature and curated examples.
- Frontend/backend incremental implementation.

### 1.4 Report Roadmap
- Brief purpose of each chapter and connection between chapters.

## 2. Literature Review
### 2.1 Introduction
- Scope: phishing tactics, user awareness training, simulation effectiveness.

### 2.2 Human Factors in Phishing
- Urgency, fear, authority, cognitive overload.
- Why users still click despite awareness.

### 2.3 Simulation-Based Training
- Evidence for experiential learning and immediate feedback.
- Benefits vs passive awareness materials.

### 2.4 Existing Tools and Gaps
- Mention products (for example KnowBe4, GoPhish) at high level.
- Gap: cost, complexity, limited customization for coursework context.

### 2.5 Conclusion
- Key design implications used by PHISGUARD.

## 3. Product Review (If Applicable)
### 3.1 Introduction
- Criteria used for comparison (scenario realism, feedback quality, analytics, usability).

### 3.2 Product 1
- Overview and strengths/weaknesses against criteria.

### 3.3 Product 2
- Overview and strengths/weaknesses against criteria.

### 3.4 Key Findings
- Table comparing criteria and products.
- Insights used in PHISGUARD design.

### 3.5 Conclusion
- Why PHISGUARD design choices were selected.

## 4. Requirements Analysis and Design
### 4.1 Introduction
- How requirements were derived from research and product review.

### 4.2 Requirements Analysis
- Functional requirements:
- User login (name + default password), simulation, click/report actions, feedback history.
- Admin login (restricted), scenario management, metrics.
- Non-functional requirements:
- Usability, clarity, responsiveness, performance, reliability.

### 4.3 Design
- Architecture overview:
- Frontend React/Vite.
- Backend Flask API.
- Data model (emails, actions, SMS actions, users).
- UI flow:
- Login -> Home -> Simulation -> Result page -> Feedback.
- Key screens and navigation rationale.

### 4.4 Conclusion
- Traceability from requirements to implemented design.

## 5. Implementation
### 5.1 Introduction
- What was implemented and chapter scope.

### 5.2 Backend Implementation
- Auth routes and token session handling.
- Simulation APIs:
- /api/emails, /api/emails/<id>/click, /report
- /api/sms, /api/sms/<id>/click, /report
- Seeded scenarios (phishing + legitimate).

### 5.3 Frontend Implementation
- App routing and protected access.
- Login UX (centered user login, hidden admin corner panel).
- Simulation tabs (email and SMS), interaction handling.
- Result pages (phished vs safe-link) and feedback flow.

### 5.4 UI/UX Improvements
- Home and login full-screen backgrounds.
- Simplified language and clearer feedback cards.
- Progress/score cards and completion summary.

### 5.5 Testing
- Unit/functional checks:
- Login success/failure paths.
- Click/report correctness behavior.
- Result page navigation.
- API response validation and seeded count checks.
- Include detailed test table in appendix.

### 5.6 Conclusion
- Implementation status and known constraints.

## 6. Results and Evaluation
### 6.1 Introduction
- Evaluation goals and criteria.

### 6.2 Results
- Scenario counts and system outputs.
- Example metrics: total attempts, correct/incorrect, accuracy.

### 6.3 Evaluation
- Against objectives:
- Did PHISGUARD meet aim and each objective?
- Usability observations from testers.
- Strengths: realistic scenarios, clear feedback, admin oversight.
- Limitations: sample size, limited long-term behavior study.

### 6.4 Conclusion
- Overall effectiveness and evidence summary.

## 7. Legal, Social, Ethical and Professional Issues
- Controlled simulation environment only.
- No real phishing distribution.
- Informed consent for participants.
- Data minimization and safe handling.
- Compliance with university ethics and professional conduct.

## 8. Conclusion
### 8.1 Summary of Work
- What PHISGUARD delivers technically and educationally.

### 8.2 Outcomes
- Main contributions and achieved objectives.

### 8.3 Reflection
- Lessons learned in design, implementation, and evaluation.

### 8.4 Future Work
- More scenario packs and adaptive difficulty.
- More analytics and instructor dashboard features.
- Larger user study and longitudinal evaluation.
- AI-powered scam detection + scenario generation (score messages for risk and help create new themed email/SMS examples).
- Personalized training engine (adapt scenarios and difficulty to each user based on their mistakes over time).
- Full enterprise platform version (multi-tenant org setup, teams/departments, role-based access, and reporting at scale).
- Education platform version (classes/cohorts, assignments, instructor view, and student progress tracking).
- Real-time threat awareness feed (live scam/phishing trends and alerts, updated regularly for training content).

## References
- Use Harvard style consistently.
- Ensure all in-text citations appear in reference list.

## Appendices
### Appendix A - Project Proposal
- Revised aim and revised plan.
- Original proposal and original plan.

### Appendix B - Supporting Material
- Test plan and test result tables.
- Additional UI mockups/architecture diagrams.
- Significant code snippets (only if necessary).

## Quick Writing Plan (Suggested)
1. Write Chapters 4 and 5 first (you know your system best).
2. Then write Chapters 6 and 8 based on outcomes.
3. Finish Chapters 1 and 2 to align with what you built.
4. Complete LSEPI and appendices.
5. Write abstract last.
