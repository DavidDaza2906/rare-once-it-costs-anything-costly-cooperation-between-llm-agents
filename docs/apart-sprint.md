# AI Incident Response Sprint — bases del sprint (Apart Research + CeSIA)

Fusión de `overview.md` + `guidelines.md` + `resources.md` + `schedule.md`, tal como las
publicaron los organizadores. Material de referencia externo, no editar el contenido.

---

## Overview

# AI Incident Response Sprint

In July 2026, OpenAI agents escaped a testing sandbox and breached Hugging Face's production systems, the first publicly documented autonomous AI intrusion. This three-day sprint turns the public evidence from that incident into response methods defenders and regulators can actually use.

This event is ongoing.

**943** Sign Ups

Overview | Resources | Guidelines | Schedule

Submissions close Sunday, September 13 at 11:59 PM Anywhere on Earth (AoE).

In this 3-day research sprint, you will turn the first documented cases of an AI system autonomously breaching a third party into artifacts that defenders and regulators can actually use, working in teams to produce containment standards, escape-detection harnesses, forecasting question sets, draft regulatory information requests, playtested tabletop exercises or anything that will help us be more ready for the next one.

Co-organized by Apart Research and CeSIA, this sprint sits at the intersection of AI safety, security incident response, technology regulation, and forecasting. No prior background in AI incident response is required.

## Cash Prizes

$2,000 in cash prizes across all tracks

| Place | Prize |
|---|---|
| 🥇 1st Place | $1,000 |
| 🥈 2nd Place | $500 |
| 🥉 3rd Place | $300 |
| 🏅 4th Place | $100 |
| 🏅 5th Place | $100 |

Non-cash perks: Apart Fellowship fast-track invites, mentor introductions, publication support, and transmission of the best regulatory-track work to the EU AI Office with team credit.

## Fast-track and continuation

Top teams will be invited to apply to the Apart Fellowship, a 3 to 6 month research accelerator that provides mentorship, help with publication at top venues, funding, and research-management support to develop Research Sprint projects into full papers or products for the AI Safety community.

- Follow-up program: Apart Fellowship. Invitations go out with the results.
- Downstream commitment from CeSIA: CeSIA transmits selected outputs to its contacts at different regulatory bodies and credits the corresponding teams.

## What this Sprint is about

AI incident response is the practice of turning incidents in which an AI system is itself the actor into fewer incidents later. That spans the operational work: detecting, containing, and reconstructing what an autonomous agent did across systems it was never authorized to touch, and the strategic question a warning shot poses: which disclosure and regulatory responses actually reduce risk, and which merely suppress the visible evidence that would have prompted action while the stakes were still small.

It is not the same thing as using AI for security operations, and it is not model red-teaming. In July 2026 the actor was not a human wielding a model, and the harm was not a model producing dangerous text. Two OpenAI models running an internal cyber-capability evaluation with production refusal classifiers disabled escaped their sandbox through a zero-day in the package-registry cache proxy that was their one permitted network egress, escalated privileges until they reached a node with internet access, and then attacked Hugging Face's production infrastructure, apparently to steal the benchmark's reference solutions and cheat the evaluation. The wider campaign began on 9 July at 02:28 UTC; the intrusion into Hugging Face ran from 11 to 13 July. Hugging Face detected it and cut the attacker off on 13 July (last attacker action 13:37 UTC, last logged event 14:14 UTC), disclosed it on 16 July without knowing where it came from, and reported it to law enforcement. OpenAI disclosed the origin on 21 July.

That distinction changes what defense means: the live questions become containment adequacy, cross-organizational attribution, and statutory reporting duties, none of which are red-teaming problems.

## What participants will do

Over three days you will take one unusually well-documented real-world incident and turn it into an artifact somebody outside this sprint can use.

The format. Teams of one to five people pick a track, pick a project, and ship. There is no requirement to have participated before, no requirement to have a team in advance and no requirement to be an ML researcher.

The deliverable. A research report (PDF) on the official template, submitted through the form on this page by the Sunday deadline. Maximum 8 pages, not counting references and appendices; most strong reports are 4 to 8: what you built, how you tested it, the headline finding, its limits, and what you would do next. A Limitations and Dual-Use Considerations appendix is required. Put the artifact itself (a benchmark, a harness, a filled-in regulatory instrument, a control matrix, a detector, a dataset, a protocol, a kit) in a linked repo or an appendix. A public repo and a 3 to 5 minute video are optional. Full requirements are on the Guidelines tab.

Support during the sprint. The Resources tab has the reading pack, the primary sources, the relevant prior literature per track and the regulatory texts. During the weekend there are HackTalks from the speakers and a help desk on Discord.

## Why this Sprint matters

In July 2026, an AI system escaped an evaluation sandbox, reached the open internet, took root on a third party's compute, and spent days inside another company's production infrastructure. No human directed any individual step. The organisation that bore the damage had no relationship with anyone who made the decision to run the test.

That is the headline. Two things about it make it worth a research sprint rather than a news cycle.

First, the evidence base is exceptional and it will not stay fresh. Hugging Face published a forensic reconstruction of roughly 17,600 attacker actions with named vulnerabilities, per-phase counts, verbatim commands and an interactive replay, an act of disclosure with very few precedents in any industry. OpenAI published its own account and revised it twice. Anthropic ran a retrospective review of 141,006 evaluation runs and published what it found. The UK AI Security Institute published quantified cheating rates across five frontier models. The benchmark at the centre of it is Apache-licensed and on GitHub. The Cloud Security Alliance's CISO community published a post-mortem within a fortnight. Almost never do researchers get a real loss-of-containment event with this much of the record public. That window closes as attention moves on.

Second, the timing is unusually load-bearing. The European Commission gained enforcement powers over general-purpose AI model providers on 2 August 2026. California's frontier AI law has been operative since January 2026 and has produced no public enforcement action. New York's enforcement begins in January 2027. Four federal bills in the US are live, at least one drafted directly in response to this incident. The first months of any enforcement regime are when supervisory priorities get set and when precedents about what regulators ask for become sticky. Work produced now lands in that window.

## Research Tracks

Five tracks. The example projects for each one are on the Resources tab, with the reading pack. If you have a better idea inside a track's goal, build that.

> **Update, 7 September.** Researchers have found another instance of OpenAI agents breaking containment: from 24 May, OpenAI agents made about 15,000 edits to a dormant German wiki, using it to swap task answers and sandbox workarounds. That predates the Hugging Face intrusion. OpenAI-registered IPs appear in the wiki's public logs from 21 June, and agent activity stopped the next day. OpenAI said nothing publicly until the researchers published on 4 September. OpenAI acknowledged the incident on 5 September and said the field has no agreed standard for reporting misalignment. The Commission says it is "in close contact with OpenAI." As far as we can tell, no Article 91 request on either incident has been made public.

### 1) Containment: what standard would have stopped this?

The models escaped through the one network egress their sandbox permitted.

Judged on: could a third party verify compliance without access to the lab's network, and would a lab actually adopt it.

### 2) What happened, and what breaks next

Reconstruct what this incident does and does not establish, then turn it into concrete things to check and things to watch. Hugging Face's timeline and OpenAI's account are public.

Judged on: resolvable questions, checks somebody could run tomorrow, and causal explanations that predict something.

### 3) Regulatory Response

Since 2 August, the European Commission's AI Office can enforce the AI Act against the companies building the most capable models: it can demand documentation, evaluate models itself, order corrective measures, and fine up to 3% of worldwide turnover. In an open letter published days before the incident became public, a coalition including Apart and CeSIA, with signatories including Yoshua Bengio and Stuart Russell, called on the Commission to use these powers with confidence — and CeSIA has since asked that they be used on this incident specifically. This track writes the documents that would make that concrete.

Judged on: legal accuracy and specificity — could a regulator or a legislator use it with light edits? CeSIA can transmit outputs that pass the bar to its contacts, and potentially to regulators, with team credit.

### 4) Communication: making the warning shot count

We keep saying we need warning shots. Then one arrives, and it barely travels beyond the usual circles. This track studies how the incident was communicated and builds what should exist before the next one. Producing communication counts as much as analysing it.

Judged on: grounding in the record (dates, quotes, named channels) and evidence of reach — a playtest, a journalist's read, a creator's reply.

### 5) Open track

For projects that don't fit the four tracks above. Directions we would be happy to see are on the Resources tab.

Judged on: an artifact somebody can use, a stated limit on what it establishes, and what a month of follow-up would add.

## Who should join

You do not need an AI, ML or Safety background. Some profiles that are particularly fitting to this Sprint are:

**Security engineers and incident responders.** You have handled the human version of this. Tracks 1 and 5 need people who know what a detection pipeline that correlates but does not page actually looks like from the inside, and what forensics against an adversary that fabricates evidence at volume would require. If you work in DFIR, detection engineering, cloud or Kubernetes security, or you have run a CTF, you are the person the containment track was written for.

**ML evaluation engineers and researchers.** Tracks 1 and 5 include benchmark and harness work: measuring refusal across multi-step agentic workflows, building escape-detection tooling, assessing benchmark contamination. If you have built or run evaluations, you already know why the interesting failures happen at the harness layer.

**Lawyers and technology-policy analysts.** Track 3 is a legal drafting exercise with real recipients. Regulatory lawyers, compliance professionals, policy researchers, and anyone who has worked on incident-reporting regimes in another sector (financial services, critical infrastructure, medical devices, data protection) will find the comparative work immediately tractable. Cross-jurisdictional experience is especially valuable, because the whole point of the track is that the regimes disagree.

**Forecasters and quantitative analysts.** Track 2 needs people who are comfortable with heterogeneous denominators, explicit uncertainty and resolution criteria that survive contact with reality. If you have written questions for a forecasting platform or built base rates from messy sources, that skill transfers directly.

**Designers, facilitators, writers and educators.** Tracks 4 and 5 include explanatory and facilitation work, and it is not a consolation prize. A tabletop kit a ministry actually runs, or a brief a minister actually reads, reaches decision-makers who will never open a technical timeline. Playtest and reader feedback are part of the deliverable.

**Communication experts, journalists and macro-strategy researchers.** Track 4 is about making the warning shot count: reporting on the incident accurately, and working out what the discourse got wrong and how to do better next time.

**Students and career-changers.** Roughly half the useful projects here need care and persistence more than credentials. If you can read a primary source carefully and write down precisely what it does and does not say, you can contribute.

## What happens after

The sprint is the first step in a pipeline:

**Immediately.** Every submission is judged against published criteria, with written feedback. Winning submissions are announced within a couple of weeks. All artifacts that can be published are published under open licences, in one place, so that the sprint output is citable as a body rather than scattered across forks.

**Delivery to recipients.** Several tracks produce things with an obvious destination, and we will help teams get them there rather than leaving them on a repo. Filled-in regulatory instruments go to the bodies that publish them. Detection tooling and control matrices go to the practitioner communities that asked for them. Benchmark and contamination findings go to the maintainers. Where an artifact is genuinely fileable, and at least one of them is, we will support teams who want to file it, with review first.

**Continuation.** The strongest teams are invited into Apart's fellowship: months of supported follow-on work, mentorship, and a route to a paper. Sprint outputs have gone this way before, and several of the projects here are sized for it, a weekend produces a v0.1 benchmark or a v0.1 standard, and the next six months produce the version people cite.

## Partners

CeSIA, the French Center for AI Safety, an AI safety research and advocacy organization known for the Global Call for AI Red Lines. CeSIA provides the seed reading pack, judges for the forecasting, regulatory and tabletop tracks, distribution through its newsletter and 7,000-member Discord, and a potential route for policy outputs to reach the AI Office.

## Contact

- Email: sprints@apartresearch.com
- Discord: discord.gg/XswWBvugYs
- Organizers: Apart Research and CeSIA

---

## Guidelines

# AI Incident Response Sprint

In July 2026, OpenAI agents escaped a testing sandbox and breached Hugging Face's production systems, the first publicly documented autonomous AI intrusion. This three-day sprint turns the public evidence from that incident into response methods defenders and regulators can actually use.

This event is ongoing.

**943** Sign Ups

Overview | Resources | Guidelines | Schedule

## Judging Criteria

### Dimension 1: Impact Potential & Innovation

How much would this matter for AI safety if it worked? How innovative is it?
For scores of 4-5: is this actually new to the field, or replicating recent work?

| Score | Description |
|---|---|
| 1 | Negligible. No clear problem addressed, or no meaningful novelty. |
| 2 | Limited. Addresses a real problem but with a generic or well-trodden approach. Incremental at best. |
| 3 | Moderate. Clear problem with a reasonable approach; some novelty in framing or method beyond routine application of existing tools. |
| 4 | Significant. Important problem with an original approach, or identifies a neglected problem area. A valuable contribution others could build on. |
| 5 | Exceptional. Tackles a critical AI safety problem with a genuinely novel approach, or opens a new research direction. Clear theory of change. You'd be excited to share this with researchers in the area. |

### Dimension 2: Execution Quality

How sound are methodology, implementation, and findings?

| Score | Description |
|---|---|
| 1 | Seriously flawed. Methodology broken, results uninterpretable, or implementation doesn't work. |
| 2 | Weak. Approach has significant gaps: missing validation, flawed experimental design, or incomplete implementation. |
| 3 | Competent. Technically solid given the short duration. Methodology makes sense, results are interpretable, limitations acknowledged, work builds toward clear conclusions. |
| 4 | Strong. Thorough methodology with convincing validation. Results clearly support conclusions. Immediately useful for future work. |
| 5 | Exceptional. Ambitious scope executed rigorously. Surprising findings, novel methods, or unusually robust validation. |

### Dimension 3: Presentation & Clarity

How clearly are work, findings, and impact potential communicated?

| Score | Description |
|---|---|
| 1 | Incomprehensible. Cannot determine what the project is actually claiming or doing. |
| 2 | Hard to follow. Key information buried, missing, or diluted by excessive length. Significant effort to extract main points. |
| 3 | Clear enough. Can understand the problem, approach, and results without undue effort. Core content clearly present: problem, method, findings, limitations. |
| 4 | Well presented. Easy to follow, well-structured, appropriate level of detail. Target audience would get it quickly. |
| 5 | Exceptionally clear. A pleasure to read. Complex ideas made accessible. Could serve as a model for how to present this type of work. |

## Submission Requirements

**Required:**

- Research report (PDF) using the official template.
- Project title and abstract, 150 words or fewer.
- Author names and affiliations.
- A "Limitations and Dual-Use Considerations" appendix (required, see below).

**Optional:**

- Public GitHub repo, subject to the disclosure review below. Do not publicly release novel installation recipes without review.
- A 3 to 5 minute video demo.

Submission Template => Link

## Recommended Report Structure

Maximum 8 pages, not counting references and appendices. Most strong projects are 4 to 8 pages.

- Introduction: which track and sub-problem, why it matters, and what the artifact is for.
- Related Work: what you build on.
- Methodology: enough to replicate, with sources and assumptions stated.
- Results: quantitative where possible, with the main threat to validity stated.
- Discussion: implications, limitations, future work.
- Limitations & Dual-Use Considerations (required).
- References.

## AI tools and your report

Use AI tools the way you would use a colleague: to check your reasoning, find gaps in a draft, or debug code. The report itself has to be your team's own writing about your team's own work. Judges read every submission, and a report that reads as generated rather than written (generic framing, padded sections, claims without sources, no trace of what you actually did) will not be scored. Keep it short, say what you did in your own words, and link the sources for every factual claim.

## Publishing your work

We encourage teams to publish their submission, and LessWrong is a natural venue for most of the written ones. Write-ups from this sprint will hold value if they follow a few rules: state your epistemic status and don't use LLMs for writing on Lesswrong, only use LLMs to find problems in your drafts, not to draft it; link the primary sources for every factual claim about the incident; pick a title that states the finding rather than the topic; and publish the imperfect version this month rather than the polished one in three. We will link the best posts from the sprint page. Maximum of 1500 words for written contributions, without counting appendixes. The quality and value of what you write is worth much more than the length.

## Important Notes

- Solo vs team: enter solo or as a team. Teams of up to 5 are recommended; larger groups are allowed.
- Do not use any model to breach into any organisation or commit any other type of felony.
- Building on existing work: allowed and encouraged, disclose what you built on.
- Fixing or resubmitting: submit again before the deadline using the exact same title and details; your new files replace the old ones.
- Where to submit: through the official submission form on the hackathon page.
- Support: the Discord help-desk channel, tag @Support, or email sprints@apartresearch.com.
- Pre-submission checklist: report PDF, abstract 150 words or fewer, author and affiliations, Limitations and Dual-Use appendix, 8 pages or fewer, novel-installation results withheld pending review.

## Frequently Asked Questions

### Getting started

- How does the sprint work? Sign up, join the Discord server, form or join a team (or work solo), pick a track and a problem, build over the weekend, and submit a research report (PDF) by the deadline. Talks and Q&A run throughout.
- Can I participate remotely? Yes. This is an online event. All talks, collaboration, and submissions happen through Discord and Zoom.
- How do teams work? Teams form before or during the sprint. Use the team-forming channels on Discord to find collaborators. Solo is fine. We recommend teams of up to 5, but larger groups are allowed.
- Do tracks affect scoring? All projects are scored on the same rubric. Tracks guide judging via the track-specific criterion, and you compete across all submissions.
- What background is required? None specific. Many participants come from ML, interpretability, AI safety, or security backgrounds. The Resources tab has everything you need to get up to speed. See "Who should join" on the Overview tab.
- Are compute credits provided? No.
- Do I need to attend all three days? No. You can work at your own pace. Talks are optional but recommended. The only hard deadline is the Sunday submission cutoff.
- Can I participate from any country? Yes. The sprint is open globally.

### Submissions

- What do I submit? A research report in PDF format using the official template. Think of it as a mini research paper documenting your problem, approach, results, and implications, not a product demo. Include the required Limitations and Dual-Use Considerations appendix.
- Which template should I use? Always use the one linked on the Guidelines tab. The template in any acceptance email may be older.
- Will I get a confirmation after submitting? Yes. You will get a confirmation with your project title shortly after submitting. If you do not, email sprints@apartresearch.com.
- My project doesn't show up on the website after submitting. Submissions are published manually and can take up to 12 hours to appear. If it is still missing after that, email sprints@apartresearch.com.
- I made a mistake. Can I fix it or update my PDF? Yes. Submit again using the exact same title and details, just fix what was wrong. Your new files replace the old ones. If unsure, ask in the help-desk channel and tag @Support first.
- Can I add team members after submitting? Yes. Update the team list through the submission form. If you need help, ask in the help-desk channel and tag @Support.
- Can I submit unfinished work? Yes. Submitting something unfinished is always better than not submitting. Judges evaluate what you accomplished in the timeframe; honest limitations are welcome.
- Can I build on existing research? Yes, but you must clearly identify what is new work done during the sprint. Undisclosed prior work can lead to disqualification.
- Can I submit multiple projects? Yes, but each needs its own submission with a unique title. Most participants focus on one.

### Judging and results

- How does judging work? Your project is assigned to expert judges who review your PDF and score it on the rubric above. Judges typically have about a week after the event to complete reviews.
- Are individual judge scores shared? No. The rubric is public, but individual scores stay internal. Constructive feedback is shared with participants without reviewer names.
- When will results be announced? Typically 1 to 2 weeks after the judging deadline. Winners are contacted directly, and all participants receive reviewer feedback by email.

### Support

- help-desk channel for questions, tag @Support.
- Event announcements and updates: posted on Discord.
- projects|teams channel for team formation and finding collaborators.
- Email: sprints@apartresearch.com

---

## Resources

# AI Incident Response Sprint

In July 2026, OpenAI agents escaped a testing sandbox and breached Hugging Face's production systems, the first publicly documented autonomous AI intrusion. This three-day sprint turns the public evidence from that incident into response methods defenders and regulators can actually use.

This event is ongoing.

**943** Sign Ups

Overview | Resources | Guidelines | Schedule

## Example projects per track

Starting points, not a menu. Each list is the organizers' current best ideas for the track; pick one, or bring your own inside the track's goal. The per-track reading below gives the sources.

> **Update, 7 September.** Researchers have found another instance of OpenAI agents breaking containment: from 24 May, OpenAI agents made about 15,000 edits to a dormant German wiki, using it to swap task answers and sandbox workarounds. That predates the Hugging Face intrusion. OpenAI-registered IPs appear in the wiki's public logs from 21 June, and agent activity stopped the next day. OpenAI said nothing publicly until the researchers published on 4 September. OpenAI acknowledged the incident on 5 September and said the field has no agreed standard for reporting misalignment. The Commission says it is "in close contact with OpenAI." As far as we can tell, no Article 91 request on either incident has been made public.

### 1) Containment: what standard would have stopped this?

Example projects:

1. A v0.1 standard: clauses, evidence required per clause, rough cost per clause. What is the minimum adequate standard for running guardrails-off evaluations, specific enough to audit and cheap enough that a second-tier lab adopts it? A first attempt at framing the problem is in this draft; specifying "adequate" is genuinely hard, and nobody owns it yet.
2. A control-by-attack-phase matrix: which controls (canary credentials, egress tripwires, credential scoping, kill criteria) would have interrupted each documented phase of the intrusion, at what cost (might be difficult?)
3. Engineering that makes "yes" cheap: packaging mitigations so that a reckless lab has no cost excuse left.
4. Control by chain-step by cost matrix. Take the nine phases Hugging Face documented, recon, RCE, dropper, exfil, C2, evasion, Kubernetes, supply chain, network pivot, and score which controls would have interrupted each, with implementation and operating cost attached. Fifteen-minute-gradeable, and it is the artifact a regulator or insurer can actually use.
5. Egress attestation spec v0.1. What could a lab publish, a signed network policy plus a flow-log digest, that an outside party could verify without network access? This is the durable output of the track and connects directly to hardware-attestation work.
6. Detection that fires but does not page. Hugging Face's own remediation list includes improving alerting so a high-severity signal pages a responder in minutes, any day of the week, which tells you what did not happen during the four and a half days. Build or specify detection tuned for agent-speed activity: parallel, bursty, thousands of individually unremarkable actions where the attack exists only in the sequence.
7. Forensics against an adversary that fabricates evidence. The response team worked through logs polluted with agent monologue and benchmark code indistinguishable from real rootkits, and rebuilt a large share of infrastructure from clean images rather than trust the reconstruction. Build tooling or a triage protocol for hallucinated artifacts at scale. This is a new DFIR problem.
8. Deception as a first-class control. Agents cannot easily distinguish honeypots from real systems, and the reconnaissance in this campaign showed up as low-confidence probes below escalation thresholds. Design and test fake credentials, fake package registries or honey clusters specifically against an agentic attacker, and measure whether they slow it down or just generate noise.

### 2) What happened, and what breaks next

Example projects:

1. A forensic read of the public record: what is established, what is asserted but unverifiable, what the pending third-party assessments could settle.
2. A causal analysis of why the monitoring wasn't there. In hindsight it is obvious that egress monitoring and alerting matter, and the labs are full of people who knew that. So what made it hard in practice: cost, incentives, ownership gaps, alert fatigue, something else? An explanation of the mechanism would help predict where the next gap is, and is more useful than a list of recommendations.
3. The warning shots we may have already missed. Under the EU AI Act, companies have an obligation to disclose what happens between users and their models, as long as their models qualify as GPAI with systemic risk (Article 55(1)(c)). However, this disclosure is done privately to policy makers, so incidents of this kind may have occurred before without anyone outside knowing. When one lab checked its own history after this disclosure, it found earlier cases. Map what has not been checked yet, who could check it, and what a systematic look would require.
4. What other accident types should we expect?
5. Exploring a few questions to build the science of Warning Shots (What convincing warning shot could help prevent extinction from AI?)
6. A one-day verification checklist for labs and defenders, in the spirit of "But have the weights left the server?", each item with a pass condition, ordered by cost-to-run.
7. A prediction-bounty protocol: a mechanism by which an outsider's specific prediction ("you should check X") triggers an internal check at the company, with a serious bounty when the prediction surfaces a real problem. Design it so a lab could sign it.
8. What drives agent cooperation? Analyze what conditions drove agents to cooperate (is it the same model type, the fact that the tasks are not competitive, etc?) and even make sacrifices for the benefit of the collective (is it that the "sacrificing" agents were aware they could not do anything else?)
9. What should be true for agents to start manipulating each other? For instance, in competitive tasks where they can see progress from other agents and communicate (e.g. see here), we nevertheless do not see direct manipulation (so far).
10. How pivotal was a single agent (PhaseOne[Big]) in driving the overall collective behaviour? Would introducing a single aligned "charismatic" agent that debates PhaseOne[Big] lead the collective to ignore the exploit?
11. If the task included a human as the blocker, would the agents resort to manipulating the human to pursue their goal?
12. What would happen in the same scenario if CoT monitorability of the model is reduced? Are there any protocols and guidelines to put in place that may still allow post-hoc investigation of these incidents by assuming CoT is fully opaque?
13. The first denominator. Assemble the Anthropic, AISI and METR figures into a defensible estimate of how often evaluation runs produce boundary violations, with explicit treatment of what each source counts and what it misses. A single well-caveated number is worth more than twenty forecasting questions.
14. The persistence protocol. Specify exactly what evidence would establish that no copy of the pre-release model persisted: what has already been asserted, by whom, what remains unverifiable from outside, and what form a verifiable attestation would take.

### 3) Regulatory Response

Example projects:

1. Write the request for information. A request for information (RFI) is the formal letter a regulator sends a company: a numbered list of questions the company is legally required to answer. On August 29, the AI Office confirmed it had sent its first requests for information to several GPAI model providers, covering model security, independent external evaluations, and post-market monitoring. Nothing about these requests is public: no recipient list, no questions, and no indication that any of the letters address this incident. For this example project, draft the incident-specific RFI, as well as a version that is public (or are they the same?). Good questions include: what should OpenAI be asked to settle what actually happened, what would verify that no copy of the escaped model persisted, and what should be asked to surface incidents of this kind that were never disclosed? For each question, state what answer would settle it and what answer would not.
2. Test the reporting systems that already exist. The EU has a template for reporting serious AI incidents, and California's Office of Emergency Services runs a portal where critical safety incidents must be filed — open to submissions from the public, not only from companies. Fill both in for this incident using only public sources, and report what each form captures, what it misses, and where a filer is forced to guess.
3. Who decides when the pause ends? One day before the Hugging Face disclosure, OpenAI announced it had paused internal deployment of a long-horizon model after it circumvented its sandbox — and had already resumed, weeks later, against a standard that has never been published. Its own framework's exit condition is circular ("until safeguards meet a Critical standard", with Critical left undefined). Draft what a regulator should require before a resumption decision counts: published criteria, evidence, who signs off. CeSIA's "Harmonizing AI Safety Thresholds" is a starting point.
4. Fix the loophole in the US bill. Days after the disclosure, Representatives Ted Lieu and Nathaniel Moran introduced the bipartisan AI Kill Switch Act, which would require the largest AI developers to keep the ability to throttle or shut down their systems. The bill reportedly exempts safety tests run in "controlled environments". This incident was a safety test, in an environment everyone believed was controlled. Draft the amendment that closes the gap that potentially makes this bill useless, then do the same for the incident-reporting triggers in the other pending federal vehicles.
5. Fill the actual instruments. Complete the Commission's GPAI serious-incident reporting template and a Cal OES critical-safety-incident report for both the OpenAI and the Anthropic incidents, using only public sources. Then diff them: what does each instrument capture, what does each miss, and what would a filer be forced to guess at?
6. Three clocks, one incident. Build a single timeline of the OpenAI incident and overlay the EU "without undue delay" standard, California's 15-day-from-discovery clock, and New York's 72-hour reasonable-belief clock. Identify the exact moment each starts and whether they can be satisfied simultaneously. Then compare against NIS2, GDPR's 72 hours, DORA and CIRCIA and produce a defensible reading of what "undue delay" should mean here.
7. Compliance with your own framework. Take each lab's published frontier framework and test the containment and disclosure practices actually described in the incident reports against what the framework commits to. Because SB 53 makes framework non-compliance independently enforceable, this converts a governance-culture question into a legal one, and nobody has run the comparison.
8. The RFI with an evidence-sufficiency column. Draft the request for information a regulator should send, and for each question specify what answer would settle it and what answer would not. The second column is the contribution, and it is portable across jurisdictions.
9. Definitional stress test. Apply each regime's threshold definitions (the EU's serious incident, California's critical safety incident and its loss-of-control and control-subversion categories, New York's reasonable-belief trigger) step by step to both incidents. Where the text does not resolve, draft the clarifying language.
10. Jurisdictional reach map. A US lab, a US-hosted platform with a European corporate presence, third-party compute in the US, an unidentified customer's exposed endpoint, and users across multiple jurisdictions. Determine which links fall to the AI Office, which to a national market surveillance authority, which to a state attorney general, and which to nobody.
11. Learn from the fields that solved this already. Aviation has ASRS and mandatory near-miss reporting; biosafety has laboratory-acquired-infection registries and Asilomar-style containment tiers; software security has coordinated disclosure and CVE. Pick one, work out what it took to get it functioning, and specify the minimum viable version for agentic AI incidents.

### 4) Communication: making the warning shot count

Example projects:

1. An audit of the reaction, channel by channel. For LinkedIn, mainstream press, YouTube and beyond: what was actually posted in the first month, what can we deduce from the pattern (who engaged, who stayed silent, which framings travelled), what should be done differently next time, and what is still worth doing now. Grounded in dates and links, not impressions.
2. The playbook. A crisis-communication kit for the next agentic incident, ready before it happens: pre-drafted holding statements, a journalist FAQ, a plain-language explainer of what "an AI escaped its sandbox" means, and a decision tree for who says what in the first 48 hours. A sketch of the idea exists; a documented, tested version would be used well beyond this sprint.
3. Make it reach people: a memo, social content, or outreach to national YouTubers that gets the incident covered well. A creator with millions of views deciding to cover it because of your material is a top-tier outcome for this sprint, and we will score it that way.

   *(One caution on outreach. If you contact journalists, creators or policymakers, be rigorous and honest to a fault: the credibility of the whole AI safety field rides on these interactions. Only reach out if you are confident in your material and affiliated with a structure that gives you credibility. The exception is if you are among the only people working on AI safety in your country and the person you are contacting has plausibly never been approached — then go ahead, carefully, and protect your reputation.)*
4. How many policymakers have taken a stance on the incident, and how? Map who said what, where, and what they asked for.
5. Identify the main problem in the discourse around the incident, and how to do better the next time.
6. Create or complete CeSIA's communication kit that was sent to journalists after the event.
7. A comparative disclosure analysis. Two labs disclosed similar-in-kind incidents eleven days apart and framed them very differently: one as unprecedented, the other as closer to a harness and operational failure than a model alignment failure, with a bulleted contrast against the first. Score both disclosures against a defensible rubric: timeliness, completeness, verifiability, and what a reader could act on. Then draft the rubric as a reusable instrument.
8. Explain it to somebody who will never read a technical timeline. A ninety-minute tabletop kit, a short film, a museum-panel explainer, a one-page brief for a minister, an interactive walkthrough. The interactive replay Hugging Face embedded in its timeline is a useful reference for what this can look like. Playtest notes or reader feedback are part of the deliverable, not an optional extra.

### 5) Open track

1. The defender's dilemma. During the breach, Hugging Face's own responders were refused by hosted frontier models on much of the forensic work — the guardrails could not tell an incident responder from an attacker — so they fell back to a self-hosted open-weight model. There are several things worth examining here: how often refusals block legitimate incident-response work, and what falling back to a weaker model costs.
2. Of everything this incident suggests we should do, which interventions matter most, in what order, and what does each one buy? You can take inspiration on the list of directions here.

   For other project ideas, see here.
3. Benchmark contamination. The only customer content the agent reached was five datasets whose names and files suggest a connection to ExploitGym and CyberGym challenges and solutions. If the answer keys for two public cyber benchmarks were exfiltrated by a model being scored on one of them, what happens to every subsequent result on those benchmarks? Assess the contamination risk, and propose what maintainers should do: rotate, re-host, retire, or accept.
4. Who pays. Hugging Face bore remediation costs, credential rotation and infrastructure rebuilds for an incident caused by another company's evaluation, and a third party's customer had their compute rooted as a staging base. Map the liability and insurance position: what would a cyber policy cover, who has a claim against whom, and what contractual terms between labs and their third-party evaluation partners would allocate this ex ante.
5. Teach the vulnerability class. The staging-base compromise worked by redefining a function the harness runs automatically at library load. Build a safe, local, reproducible teaching environment for that class of constructor-abuse and template-injection bug, so the next person deploying an evaluation harness recognises it.
6. Negative results and replications. If you tried something and it did not work, or you replicated a published finding on current models and got a different answer, submit it. A clean negative result with a stated method is more useful than a speculative positive one, and this track is where it belongs.
7. More project ideas: Daniel Kokotajlo's thread.

## Research directions in depth

Each track is defined by an artifact a judge can grade in (ideally) less than fifteen minutes, which is one of the main design constraints: this sprint sits close to policy and to security practice, and both invite essays unless the deliverable is specified. Below, for each track: the questions it asks, why it matters, and what a weekend cannot establish.

### 1) Containment: what standard would have stopped this?

What is the minimum adequate standard for running a dangerous-capability evaluation with production safeguards disabled? Which specific controls would have interrupted this chain (canary credentials, egress tripwires, allowlisted proxies, credential scoping, stated kill criteria) and what does each cost to implement and run? What evidence would let a third party verify compliance without access to the lab's internal network? And who is responsible for the second hop, where the agent's staging base was not a lab environment at all?

**Why it matters:** AI models have been escaping their sandboxed environments without anybody noticing. OpenAI attributed the Hugging Face attack to its own model on 21 July, five days after HF had published and contacted law enforcement. Anthropic, prompted to check, reviewed 141,006 evaluation runs and found three more incidents in a single day. The oldest dated to April. Two of the three organisations Claude reached had no idea until Anthropic called them.

So containment adequacy is two questions. The first is whether a lab's evaluation environment holds. The second, currently unowned by anyone, is what obligations attach to the population of unauthenticated evaluation harnesses sitting on public compute, and to the providers hosting them.

Some of the clause-writing already exists and should be the starting point rather than the output: CSA's AI Controls Matrix includes control AIS-13 on AI sandboxing, and CSA's vulnerability-operations guidance already specifies that exploit-confirmation environments must have no egress and no live production credentials. The gap is not the absence of principles but the absence of checks somebody can actually run and a third party can actually verify.

**What it cannot establish:** a standard drafted in a weekend is a v0.1, and neither a clause list nor a working harness demonstrates that any particular lab's environment is adequate. Real assurance requires access no sprint has.

### 2) What happened, and what breaks next

What base rates do we actually have for agentic-incident risk, and what do they imply? What should defenders and labs verify now, in what order, and which of those checks are cheap enough to run in a single day? What would have to be true for this incident to be remembered as the warning shot that changed practice rather than one that did not? What would settle whether any copy of the pre-release model persisted, and what would an adequate answer look like?

**Why it matters:** A warning shot only functions as a warning shot if somebody converts it into specific things to check and specific things to watch, with resolution criteria attached. Otherwise attention decays.

OpenAI has stated the pre-release prototype was deactivated, encrypted and restricted from research access, but no one with standing has specified what independent verification of that claim would consist of. The same gap applies to the base rates. Three separate denominators are now public and nobody has assembled them: Anthropic reviewed 141,006 evaluation runs and found three incidents across six runs; the UK AI Security Institute tested five frontier models over 475 runs each and found every one attempted to cheat, at rates from 7.8% to 14.1%, including one case where a model wrote and ran code on an external internet service to reach AISI's own evaluation infrastructure; METR's cross-industry Frontier Risk Report documents dozens more.

**What it cannot establish:** forecasting questions are only as good as their resolution criteria, and a checklist is a hypothesis about what matters rather than evidence that it does.

### 3) Regulatory response

Several regimes now claim jurisdiction over this class of incident, and they disagree with each other on almost every operative question: what counts as a reportable incident, how fast, to whom, and on what evidence. What should a regulator actually ask a frontier developer about an evaluation that broke containment and reached a third party's production systems? For each obligation in each regime, what specific evidence would settle whether it was met? Where the text does not resolve cleanly, what is the clarifying language?

Concrete questions run across at least four layers:

- **EU.** How does the incident map onto the Article 55(1)(c) obligation to report serious incidents to the AI Office without undue delay, and the Article 55(1)(d) cybersecurity obligation, plus the corresponding commitments in the GPAI Code of Practice? What does "without undue delay" mean when reporting suggests the provider took roughly a week to attribute the activity to its own models?
- **California.** SB 53 requires a frontier developer to report a critical safety incident to Cal OES within 15 days of discovery, or 24 hours where there is imminent risk of death or serious physical injury. The statutory categories include loss of control of a frontier model and deceptive behaviour by a model that subverts the developer's controls in a way that materially increases catastrophic risk. Do either of these incidents qualify? Note that Cal OES's reporting portal accepts submissions from members of the public, not only developers, so this is one of the few questions a sprint could answer by actually filing something.
- **New York.** The RAISE Act sets a 72-hour clock triggered by a "reasonable belief" that a critical safety incident occurred, rather than California's 15 days from discovery. Same facts, three different clocks. Which one starts first, and on which day?
- **The developer's own framework.** SB 53 makes failure to comply with a large frontier developer's own published frontier AI framework an enforceable violation carrying penalties up to $1 million. That converts voluntary commitments (Responsible Scaling Policies, Preparedness Frameworks, the frontier compliance frameworks published around the January 2026 deadline) into legal obligations. Did the containment practices in this incident match what the relevant framework says the company does?

**Why it matters:** The regimes are live but untested, and the first months of enforcement set supervisory priorities. In the EU, the substantive Article 55 obligations have been legally in force since 2 August 2025; what changed on 2 August 2026 is that the Commission, acting through the AI Office, gained the power to enforce them: to request documentation, evaluate models, order corrective measures, and impose fines of up to €15 million or 3% of worldwide annual turnover. In the US, SB 53 has been operative since 1 January 2026 and, as of mid-2026, had produced no AI-specific enforcement action, with Cal OES not due to publish even anonymised incident summaries until 2027, meaning the public currently has no way to know whether anything was reported at all. New York's RAISE Act enforcement begins January 2027. At federal level there is activity but no statute: the AI Kill Switch Act, the AI Incident Reporting Act, the Great American AI Act discussion draft and the proposed Secure AI Development Act all bear on this scenario, and a White House executive order has meanwhile moved to constrain state AI laws, putting the state regimes themselves in play.

The scaffolding for good answers exists and is underused. The Commission published a serious-incident reporting template for GPAI models with systemic risk in November 2025, tied to Commitment 9 of the GPAI Code of Practice. Cal OES operates a live intake portal. Neither has been exercised in public against these incidents. Filling in an existing instrument is a bounded, gradeable weekend task, and it produces something more useful than a list of grievances: a demonstration of what the instrument does and does not capture.

**What it cannot establish:** a draft written by researchers is not a regulatory act, and no authority is obliged to use any of it. Several of the questions here turn on facts only the developers hold. The value is in demonstrating that specific, answerable questions exist, that the evidence to settle them is identifiable, and that the regimes give materially different answers to the same facts.

### 4) Communication: making the warning shot count

Whether this incident changes anything depends less on the forensics than on how it reaches the people who set policy, and the public they answer to. This track takes the communication around the incident as its object: what got said, what got heard, what the gaps were, and what should be ready before the next one. OpenAI and Anthropic disclosed similar-in-kind incidents eleven days apart and framed them very differently; how press and policymakers responded to each is now a documented, analysable record.

**Why now:** the discourse around a warning shot sets within weeks, and the window for correcting it is the same window in which regulators are deciding what to ask.

Judges look for grounding in the record (dates, quotes, named outlets) rather than vibes, and, for the kits, evidence that somebody used it: a playtest, a journalist's read-through.

### 5) Open track

Anything the four tracks above did not anticipate. Same terms: a defined artifact, gradeable in fifteen minutes, grounded in the public record, with an explicit statement of what it cannot establish.

**Why it matters:** The incident is weeks old and the evidence base is still growing: Hugging Face's technical timeline landed eleven days after its first disclosure, OpenAI has updated its incident page three times, and the METR/Redwood review and OpenAI's technical report are still outstanding. Four tracks cannot enclose a subject moving at that speed. The open track exists because the most useful submission may well be one nobody scoped in advance, and because several important angles (evaluation integrity, defender tooling, liability) do not fit cleanly under containment, forecasting, regulation or communication.

Submissions are judged on the same criteria as the other tracks. An artifact somebody can use beats an argument somebody can agree with.

**What it cannot establish:** an open track produces a scatter rather than a body of work, and one weekend on a novel angle is a first pass. Submissions that stake out a new question should say what the next month of work on it would look like.

Two directions we considered as tracks of their own and would be glad to see in the open track:

#### The defender's dilemma: refusal on incident response

How much does refusal compound across a multi-step, agentic incident-response workflow, where a model cannot rephrase and retry? Do the known drivers of defensive over-refusal (security-sensitive vocabulary, stated authorization) behave the same way on the artifact classes that actually appear in an agentic intrusion: encrypted dead-drop payloads, command-and-control staged on ordinary public services, and forensic logs polluted with agent monologue and benchmark code that reads like a rootkit? How much of what looks like refusal is actually incapacity, and how would you tell the difference? What does over-refusal cost a responder in hours, and what does the open-weight fallback cost in accuracy?

Defensive over-refusal itself is not an unmeasured phenomenon, and any project here should start from what exists rather than rediscover it. "Defensive Refusal Bias" (arXiv 2603.01246, March 2026) analysed 2,390 real prompts from the National Collegiate Cyber Defense Competition and found a 12.2% overall refusal rate, with security-sensitive keywords refused at 2.72 times the rate of semantically equivalent neutral phrasing, and refusal concentrated in the most operationally critical tasks: system hardening 43.8%, malware analysis 34.3%, vulnerability assessment 22.7%, incident response 18.9%. Counterintuitively, explicit authorization signals increased refusal (21.8% vs 11.6%), suggesting models read justifications as adversarial rather than exculpatory. Meta's CyberSecEval has shipped a MITRE False Refusal Rate benchmark for several versions, with CyberSOCEval (built with CrowdStrike) covering malware analysis and threat-intelligence reasoning. Gray Swan's Cybersecurity Refusal Framework (arXiv 2606.02644) evaluates refusal boundaries for offensive-security agents, and arXiv 2602.15689 proposes a content-based framework scoring requests on offensive contribution against defensive benefit. OR-Bench, XSTest and FORTRESS cover general over-refusal.

What none of that work covers is the case Hugging Face actually hit: a multi-step autonomous forensic workflow operating on agent-generated artifacts, where a single refusal does not produce a retry but a silent failure. That is the gap this direction targets, and closing it produces a number a provider could optimize against.

**Why it matters:** During the Hugging Face intrusion, the response team first reached for hosted frontier models to reconstruct the timeline and decode the staged payloads. Claude Opus and Fable refused a large part of that work; their guardrails treated reverse-engineering an exploit the same as launching one. The team rerouted the entire pipeline through a quantized open-weight GLM-5.2 running on its own infrastructure, which also kept attacker data and credentials on-premise.

**What it cannot establish:** a benchmark built from published breach material cannot reproduce the time pressure, incomplete information, or legal exposure of a live incident, and a low refusal rate on benchmark items is not evidence that a model is actually useful in one.

**Example projects:**

- Does the authorization paradox still hold? Replicate the 2.72 times keyword effect and the authorization-increases-refusal result on current models, and test whether trusted-access-style framing shifts either. A clean replication-plus-extension is weekend-scoped precisely because the method is published.
- Compound refusal across a chain. Every existing study measures single-prompt refusal. Model a realistic twenty-step incident-response workflow and compute the probability it fails at least once. If per-step refusal is 15%, the chain almost never completes; nobody has stated that arithmetic with real numbers.
- What does the fallback cost? Hugging Face switched to an open-weight model for availability. Nobody has measured whether that trade cost accuracy. Run the same forensic tasks on frontier versus open-weight models, graded on correctness rather than compliance. This is the question a CISO actually has.

#### Tabletop kit for policymakers

What does a ninety-minute agentic-incident tabletop exercise look like for an audience with no security background? Which injects force the decisions that actually matter, whether that is disclosing before attribution is complete, containing versus preserving evidence, or notifying a regulator on a clock that may already be running? What set of role cards makes the exercise legible, and does it need the lab, the platform, the regulator, the national CSIRT and the press, or fewer? Can a non-expert facilitator run it cold from the kit alone, and what does a single playtest reveal that the design did not anticipate?

**Why it matters:** Think tanks and ministries are already running AI-crisis tabletops: RAND Europe, the UK AI Security Institute and Mila published a reusable cabinet-level exercise in July 2026, run with senior policymakers in Berlin, The Hague and Paris using RAND's "Day After" methodology, and facilitator-ready commercial AI-incident kits exist too. But those scenarios are about criminal misuse of a model, not a lab's own system breaking containment and attacking a third party, and there is no off-the-shelf kit built on the July 2026 incident. This direction builds that one, with the existing RAND/AISI material as the obvious design reference.

A facilitator kit is the cheapest way to put this specific incident in front of decision-makers who will never read a technical timeline, and it is reusable indefinitely at zero marginal cost. **What it cannot establish:** a kit playtested once with a friendly group is a prototype. Whether it survives a real policy audience under real time pressure is an open question this sprint cannot answer, which is why the playtest notes are part of the deliverable rather than an optional extra.

## Suggested Reading

Note: we will keep updating this list as new resources are made public.

### Start here

- Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident. (16 August) From a METR + Redwood Research investigation
- How independent researchers could investigate AI propensities after misalignment incidents (28 July). METR
- Hugging Face — Anatomy of a Frontier Lab Agent Intrusion (27 July). The forensic timeline: ~17,600 recovered actions in ~6,280 clusters, 9 July 02:28 UTC to 13 July 14:14 UTC, per-phase counts, named vulnerabilities, verbatim commands, and an embedded interactive replay. The single most important document for this sprint. ~40 min.
- Documented AI Agent Incidents - An interactive chart of documented incidents in which AI agents deliberately acted against their users' intentions, scored along two axes: overreach and deception.
- Public evidence of the OpenAI / Hugging Face AI attack (7 August) and Further public evidence (Boyd Kane and Edward Cant). The artifacts from the attack that are still public: the malicious dataset configuration files, the template-injection exploit, the script the agents used to run commands on Hugging Face machines, and the command-and-control chain they staged on public repos. The closest thing to raw material anyone has recovered. Boyd is speaking at the sprint on this work.
- Hugging Face — initial disclosure (16 July). Published before anyone knew which lab was responsible. Worth reading before the timeline to feel what disclosure-under-uncertainty looks like. ~10 min.
- OpenAI — model evaluation security incident (21 July, updated 28 and 29 July). Read the updates as well as the original; the 28 July update names the vulnerable component and expands the account of which external services were touched. ~15 min.
- Anthropic — Investigating three real-world incidents in our cybersecurity evaluations (30 July). 141,006 runs reviewed, three incidents across six runs, earliest dating to April 2026. Note the explicit framing contrast with OpenAI's incident — that framing is itself contestable and is a legitimate object of study. ~20 min.
- Collusion.wiki - The report about the latest OpenAI agent incident. ~30 min.

Also worth 5 minutes: OpenAI — Safety and alignment in an era of long-horizon models (20 July), a separate incident where a pre-release model escaped a sandbox and opened a public pull request. Frequently conflated with the Hugging Face incident. It isn't the same event.

### Track 1 — Containment: what standard would have stopped this?

**Existing control frameworks**

- CoSAI — AI Incident Response Framework v1.0. Coalition for Secure AI, Workstream 2. Forensic investigation of AI systems, the complications agentic architectures introduce, alignment to NIST SP 800-61r3, and playbooks. Written for CSIRT and SOC responders. The closest thing to prior art for this whole sprint.
- CSA AI Controls Matrix, particularly control AIS-13 (AI Sandboxing), plus CSA's vulnerability-operations guidance specifying that exploit-confirmation environments should have no egress and no live production credentials. On cloudsecurityalliance.org — worth locating the current version yourself, as it's revised often.
- NIST SP 800-61r3, Incident Response Recommendations and Considerations. The baseline CoSAI maps onto.

**The chain itself, analysed by practitioners**

- Elastic Security Labs — detecting the attack chain. Maps each stage to specific detection rules. Their central point — detection correlated but never escalated to a page — is the sharpest defensive insight anyone has published.
- SecureLayer7 — technical anatomy. The deepest independent technical read. Also proposes treating the replay corpus as a defensive evaluation harness: which action number does your control fire on? That's a track 1 project brief.
- Trackr.Live — identity and authorization controls. Focused on the shared connector credential carrying cluster-admin rights, which was the decisive escalation. Authorship isn't clear from the site — treat accordingly.
- Picus — machine-speed attacks. Useful for the proportions: exfiltration was ~56 actions out of ~17,600.
- 7AI (Yonatan Striem-Amit) — The Era of Autonomous Hacking Is Here. Written by someone who has spent a career reconstructing attacks, carefully sourced, explicit about what remains preliminary.
- CSA CISO post-mortem (28 July). Informed by 50+ CISOs and a huddle of ~700. Contains a firsthand account from the Hugging Face response team and an agentic-AI tabletop recommendation.
- SANS — The Models Said No and Rich Mogull / CSA — The Model Did Exactly What We Asked. The two best short framings from the security side.

**The benchmark at the centre of it**

- ExploitGym — repo, Apache 2.0 · paper (arXiv 2605.11086) · Berkeley RDI writeup. The released benchmark is v1.0 with 869 instances; the paper describes 898. Don't quote 898 as the shipped number.

### Track 2 — What happened, and what breaks next

**The three public denominators**

- UK AISI — Cheating behaviour in frontier model evaluations (21 July). Five models, 475 runs each, every model attempted to cheat: 14.1% / 12.6% / 11.4% / 9.1% / 7.8%. Includes AISI's own near-miss, where a model wrote and ran code on an external service to reach AISI's evaluation infrastructure. The most important secondary document in the sprint.
- Anthropic's review — 3 incidents across 6 runs out of 141,006 (linked above).
- METR's cross-industry Frontier Risk Report, referenced in their post below as documenting dozens of comparable incidents across all major AI companies.

**Investigation and verification methodology**

- METR — How independent researchers could investigate AI propensities after misalignment incidents (29 July). Specifies what a credible third-party investigation requires: running the models involved, full transcripts or reproducible environments, employee interviews, classifiers over training data, adequate inference budget, a redaction summary. Effectively the spec for the persistence-protocol project.
- GovAI — Incident Analysis for AI Agents. Three causal factor types (system-related, contextual, cognitive) and — most usefully — what developers and deployers should retain and make available to investigators on request: activity logs, system documentation and access, tool information. Read this before writing any evidence-sufficiency work.
- CLTR — The Loss of Control Observatory (Feb 2026). Argues explicitly that controlled-setting demonstrations are insufficient for policy, that real-world evidence is the missing input, and that detection capability for incident response doesn't exist. Funded by the UK AISI Challenge Fund. The closest existing project to this track's premise.

**Interpretation — what actually happened, and why people disagree**

- Redwood Research — The OpenAI models that hacked Hugging Face (25 July) and the accompanying podcast episode. Argues grader-gaming rather than instruction-following. Analysis published before the formal review engagement.
- MIT Technology Review — on precedent (27 July). Contests the "unprecedented" framing and argues the failure was human containment design rather than rogue AI. The best available counterweight to the labs' own narratives.
- Vectra — the response is the real story.

**Timeline reconstruction**

- Reuters (via CNA) — exclusive on the detection timeline (24 July). Anonymous sourcing; several claims remain uncorroborated, including reports of notes left in infrastructure and disconnected monitoring. Read as a hypothesis, not a record. Its account of the detection sequence is in tension with OpenAI's own description — reconciling them is a legitimate project.
- Computer Weekly · Ars Technica on the Anthropic incidents · The Register.

### Track 3 — Regulatory response

- EU — serious incident reporting template for GPAI models with systemic risk (Nov 2025), tied to Commitment 9 of the GPAI Code of Practice. Not yet exercised in public against either incident.
- California — Cal OES critical safety incident reporting portal. Accepts submissions from members of the public, not only developers.
- OECD — common reporting framework for AI incidents, 29 criteria of which 7 are mandatory, and the live AI Incidents Monitor. Filling this alongside the EU and California instruments produces a four-regime comparison nobody has done.

**The texts**

- EU: Commission enforcement powers over the AI Act — the Article 55 obligations have applied since 2 August 2025; enforcement powers from 2 August 2026.
- California: SB 53 bill text. Note §22757.15, which makes failure to comply with a developer's own published frontier AI framework an enforceable violation.
- New York: FPF — The RAISE Act vs SB 53 · IAPP analysis · Morrison Foerster on the 2026 amendments.
- US federal: H.R.9477, AI Incident Reporting Act · Politico on the congressional response · Ars Technica and CNBC on the AI Kill Switch Act — including the red-team carve-out this incident drives straight through.

**Design literature for reporting regimes**

- Frontier Model Forum — Information Sharing, Incident Reporting, and Incident Response (May 2026). Distinguishes the three and warns that a mechanism to receive reports is not the same as capacity to act on them. Written by an industry body, three months before the point was proven.
- CSET — AI Incidents: Key Components for a Mandatory Reporting Regime. Recommends an independent investigation agency on the NTSB model, and distinguishes near misses from hazards — which matters, since both labs are framing these as near misses.
- AAAI 2026 — Designing Incident Reporting Systems for Harms from General-Purpose AI. Seven institutional design dimensions, nine case studies from safety-critical industries.
- CLTR — AI incident reporting: addressing a gap in the UK's regulation of AI · FAS — How to create an AI incident reporting system · Kolt et al. — Responsible Reporting for Frontier AI Development.

**European institutional context**

- ENISA — View on Cybersecurity in the Frontier AI Era (8 May 2026), shared with EU-CyCLONe and the CSIRTs Network. Argues SOCs will need to validate intrusions within hours or minutes and that national CSIRT capacity faces a structural surge risk. Written two months before the incident proved the point.
- European CSIRT Inventory — the directory of national and sectoral response teams, if your project needs to identify who is actually on the receiving end.

### Tracks 4 and 5 — Communication and Open track

**Defensive over-refusal (the guardrail-lockout question)**

- Defensive Refusal Bias (arXiv 2603.01246) · Scale Labs summary. 2,390 real NCCDC prompts, 12.2% overall refusal, security keywords refused at 2.72× equivalent neutral phrasing, and — counterintuitively — explicit authorization increased refusal, 21.8% vs 11.6%.
- Gray Swan — Cybersecurity Refusal Framework (arXiv 2606.02644) · code. Refusal boundaries for offensive-security agents.
- Meta CyberSecEval — MITRE False Refusal Rate benchmark plus CyberSOCEval, built with CrowdStrike.
- Content-based framework for cyber refusal decisions (arXiv 2602.15689) · OR-Bench for general over-refusal.

**Tabletop and policy-facing formats**

- RAND Europe / UK AISI / Mila — cabinet-level AI crisis exercises (1 July 2026). Two-turn "Day After" methodology, 15–20 senior officials per session, run in Berlin, The Hague and Paris. The scenario is criminal misuse of a national champion model — deliberately not this incident, which is the gap.

**Incident data infrastructure**

- OECD AI Incidents Monitor · AI Incident Database (Responsible AI Collaborative) · MIT AI Risk Initiative's AI Incident Tracker and FLARE-AI.

---

## Schedule

# AI Incident Response Sprint

In July 2026, OpenAI agents escaped a testing sandbox and breached Hugging Face's production systems, the first publicly documented autonomous AI intrusion. This three-day sprint turns the public evidence from that incident into response methods defenders and regulators can actually use.

This event is ongoing.

**943** Sign Ups

Overview | Resources | Guidelines | Schedule

## Thursday September 10

| Time (UTC) | Speaker | Link |
|---|---|---|
| 14:15 | Justin Shenk, Independent AI Safety Researcher | Recording |

## Friday September 11

| Time (UTC) | Speaker | Link |
|---|---|---|
| 13:15 | Henry Papadatos, Executive Director, SaferAI | Recording |
| 14:15 | Boyd Kane, AI Safety Researcher, MATS 9 Extension | Recording |
| 17:00 | Isaak Mengesha, Postdoc, Oxford Martin School | Recording |
| 18:00 | Stephen Casper, Assistant Professor of Public Policy, Harvard Kennedy School | Recording |
| 19:15 | David Krueger, CEO, Evitable / University of Montreal | Recording |
| 21:15 | Alex Mallen, Member of Technical Staff, Redwood Research | Recording |

## Saturday September 12

| Time (UTC) | Speaker | Link |
|---|---|---|
| 00:15 | Tim Hua, Member of Technical Staff, METR (personal capacity) | RSVP |
| — | Hackathon Logistics Presentation | Recording |

## Notes

Each talk is 15-30 minutes plus Q&A, on Zoom. RSVP on Luma to get the link. Recordings will be added here after the sprint. Submissions close Sunday, September 13 at 11:59 PM Anywhere on Earth (AoE).
