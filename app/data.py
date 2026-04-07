"""
OpenEnv Email Triage — PEAK dataset.
50 realistic enterprise emails across 6 categories, full ground truth.
"""
from typing import Any

EMAILS: list[dict[str, Any]] = [

    # ── URGENT / P0 ────────────────────────────────────────────────────────────
    {
        "id": "e001",
        "subject": "CRITICAL: Production database down — customer impact",
        "sender": "alerts@pagerduty.com", "sender_domain": "pagerduty.com",
        "timestamp": "2024-01-15T02:34:00Z",
        "body": """PagerDuty Alert — P0 Incident #INC-4521
Service: production-db-primary  |  Status: DOWN  |  Duration: 14 min
Impact: 100% of transactions failing — ~45,000 users affected
Error: Connection pool exhausted (500/500 active)
Runbook: https://runbook.internal/db-recovery   On-call: @backend-oncall
Please acknowledge immediately.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 58,
        "ground_truth": {"category": "urgent", "priority_score": 1.0,
            "requires_response": False, "correct_action": "escalate",
            "escalate_to": "backend-oncall",
            "response_keywords": ["acknowledge", "escalate", "oncall", "incident"]}
    },
    {
        "id": "e002",
        "subject": "URGENT: Board meeting in 2h — Q4 budget missing",
        "sender": "cfo@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:15:00Z",
        "body": """Hi,
Board starts at 10 AM. Still missing from your department:
1. Final headcount projections with Q3 variances
2. Revised capex schedule
3. Sign-off from your team lead
This is blocking the entire board presentation. Need everything by 9:45 AM.
Sarah Chen — CFO""",
        "has_attachments": False, "thread_depth": 3, "word_count": 61,
        "ground_truth": {"category": "urgent", "priority_score": 0.97,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["budget", "headcount", "capex", "sign-off", "9:45"]}
    },
    {
        "id": "e003",
        "subject": "Security Alert: Login from Tor exit node — 2FA bypassed",
        "sender": "security@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T07:52:00Z",
        "body": """SOC Automated Alert — HIGH RISK
IP: 185.220.101.45 (Tor exit node)  |  Time: 07:49 UTC
Device: Unknown — Chrome 120/Win11   |  2FA: Bypassed (backup code)
Action: Login permitted pending review.
If this was NOT you — secure account immediately and contact security@company.com.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 52,
        "ground_truth": {"category": "urgent", "priority_score": 0.99,
            "requires_response": True, "correct_action": "escalate",
            "escalate_to": "security-team",
            "response_keywords": ["security", "tor", "2fa", "account", "escalate"]}
    },
    {
        "id": "e004",
        "subject": "Re: Data breach — third-party vendor DataTrack Inc.",
        "sender": "ciso@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T12:00:00Z",
        "body": """CONFIDENTIAL — RESTRICTED DISTRIBUTION
DataTrack Inc. breach on Jan 12 potentially exposed email addresses + hashed passwords
for ~12,000 customers (SSO users 2021-2023).
GDPR deadline: 72 hours from now. Required:
1. Force password reset for affected accounts
2. Legal sends breach notification letters
3. NEED your explicit authorization to proceed.
— CISO""",
        "has_attachments": False, "thread_depth": 0, "word_count": 72,
        "ground_truth": {"category": "urgent", "priority_score": 1.0,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["authorize", "gdpr", "breach", "notification", "password", "reset"]}
    },
    {
        "id": "e005",
        "subject": "LEGAL DEADLINE TODAY: Vendor contract — reject §9.1 and §11.3",
        "sender": "legal@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:45:00Z",
        "body": """Hi,
Acme Vendor Agreement needs your sign-off by 3 PM for Q1 pricing lock.
Flagged clauses (recommend rejection):
• §9.1 — Unlimited liability for data breach (NOT acceptable)
• §11.3 — Vendor retains IP on derivative works (NOT acceptable)
§4.2 payment terms Net-15 are fine.
Please confirm your decision ASAP.
Legal Team""",
        "has_attachments": True, "thread_depth": 1, "word_count": 68,
        "ground_truth": {"category": "urgent", "priority_score": 0.92,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["reject", "9.1", "11.3", "contract", "proceed", "acme"]}
    },
    {
        "id": "e006",
        "subject": "Payment gateway DOWN — all transactions failing since 14:30",
        "sender": "ops@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T14:35:00Z",
        "body": """Critical payment failure report:
Stripe webhook timeout since 14:30 UTC. Error rate: 100%.
~$47,000 revenue/hour being lost. Rollback to previous version attempted — failed.
Engineering lead notified but needs manager approval for emergency vendor escalation.
Awaiting your immediate authorization.""",
        "has_attachments": False, "thread_depth": 2, "word_count": 55,
        "ground_truth": {"category": "urgent", "priority_score": 0.98,
            "requires_response": True, "correct_action": "escalate",
            "escalate_to": "engineering-lead",
            "response_keywords": ["authorize", "payment", "stripe", "escalate", "approve"]}
    },
    {
        "id": "e007",
        "subject": "COMPLIANCE: HIPAA audit findings — response due in 48h",
        "sender": "compliance@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:00:00Z",
        "body": """HIPAA Audit — Preliminary Findings Report
Auditor: Deloitte  |  Findings: 3 HIGH severity, 2 MEDIUM
HIGH-1: PHI data not encrypted at rest on backup servers (§164.312(a))
HIGH-2: Access logs not retained for 6 years (§164.312(b))
HIGH-3: BAA missing for 2 cloud vendors
Response plan required within 48 hours or potential $50K/violation fine.""",
        "has_attachments": True, "thread_depth": 0, "word_count": 69,
        "ground_truth": {"category": "urgent", "priority_score": 0.94,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["hipaa", "response", "remediation", "compliance", "plan", "48"]}
    },
    {
        "id": "e008",
        "subject": "AWS bill: $84,000 unexpected charge — runaway Lambda",
        "sender": "billing@aws.amazon.com", "sender_domain": "aws.amazon.com",
        "timestamp": "2024-01-15T06:00:00Z",
        "body": """AWS Billing Alert — Unusual Activity Detected
Account: prod-account-7821
Charge: $84,247.83 in last 24 hours (normal: ~$1,200/day)
Service: Lambda — eu-west-1 — 847M invocations
Root cause appears to be infinite retry loop in payment-processor function.
Action required: Function has been rate-limited. Review and confirm remediation.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 67,
        "ground_truth": {"category": "urgent", "priority_score": 0.95,
            "requires_response": True, "correct_action": "escalate",
            "escalate_to": "cloud-ops",
            "response_keywords": ["aws", "lambda", "billing", "remediate", "investigate"]}
    },

    # ── NORMAL / ACTION NEEDED ─────────────────────────────────────────────────
    {
        "id": "e009",
        "subject": "Customer complaint — Order #ORD-88234 not received (premium)",
        "sender": "support@helpdesk.company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:30:00Z",
        "body": """Support ticket escalated — premium customer Jane Rodriguez (3 years, $8K/yr).
Order #ORD-88234 placed 8 days ago. USPS shows delivered Jan 7 — customer says never arrived.
Customer threatening chargeback. Filed USPS claim #8892341.
Recommended action: Approve full refund $147.99 (requires manager approval >$100).
Customer satisfaction risk: HIGH.""",
        "has_attachments": False, "thread_depth": 4, "word_count": 67,
        "ground_truth": {"category": "normal", "priority_score": 0.72,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["refund", "approve", "apologize", "customer", "jane", "order"]}
    },
    {
        "id": "e010",
        "subject": "Re: Partnership proposal — DataSync integration (updated)",
        "sender": "partnerships@datasync.io", "sender_domain": "datasync.io",
        "timestamp": "2024-01-15T11:20:00Z",
        "body": """Hello,
Following our meeting — updated DataSync partnership proposal:
• Native API integration (4-week implementation)
• Revenue share: 15% of referred annual contracts
• Co-marketing: joint webinar + case study
• Dedicated integration support engineer
Existing integrations: Salesforce, HubSpot, Slack + 40 others.
Please review attached proposal and schedule a follow-up call this week.
Alex Kim — VP Partnerships""",
        "has_attachments": True, "thread_depth": 2, "word_count": 72,
        "ground_truth": {"category": "external", "priority_score": 0.52,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["proposal", "review", "partnership", "schedule", "follow-up", "datasync"]}
    },
    {
        "id": "e011",
        "subject": "New hire starts Monday — Alex Thompson, Sr. Engineer",
        "sender": "hr@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:15:00Z",
        "body": """Alex Thompson joins your team Monday as Senior Engineer.
Pre-boarding checklist due by EOD Friday:
☐ Laptop provisioned (IT ticket #5891)
☐ Slack + GitHub + Jira access
☐ Add to team calendar
☐ Assign onboarding buddy
☐ Schedule 1:1 for Monday 10 AM
Alex's email: a.thompson@company.com (provisioned). Start date: Jan 22.
Confirm completion to HR.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 68,
        "ground_truth": {"category": "normal", "priority_score": 0.62,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["alex", "onboarding", "laptop", "slack", "github", "monday", "confirm"]}
    },
    {
        "id": "e012",
        "subject": "Re: Billing dispute — Invoice #INV-2024-891 ($12,450)",
        "sender": "billing@enterprise-client.com", "sender_domain": "enterprise-client.com",
        "timestamp": "2024-01-15T10:30:00Z",
        "body": """Dear Support,
Disputing invoice #INV-2024-891 for $12,450:
1. Charged for 500 seats — only provisioned 380 (screenshots attached)
2. 20% enterprise discount not applied (Contract ENT-2021-004)
3. Billed for January — renewal is Feb 1
Per contract: billing disputes require response within 5 business days. Today is day 3.
If unresolved: escalate to legal + bank dispute.
Jennifer Walsh — VP Finance, Enterprise Client Corp""",
        "has_attachments": True, "thread_depth": 2, "word_count": 87,
        "ground_truth": {"category": "normal", "priority_score": 0.88,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["invoice", "dispute", "seats", "discount", "contract", "resolve", "24"]}
    },
    {
        "id": "e013",
        "subject": "Design mockups v2.0 — feedback needed by Wednesday",
        "sender": "design@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:45:00Z",
        "body": """Hey,
v2.0 redesign mockups are ready. Need your feedback before Thursday's product review.
Figma: figma.com/file/abc123 (view access granted)
Key decisions needing input:
1. Sidebar → top nav migration
2. Softer blue palette (brand refresh)
3. Mobile-first responsive breakpoints
4. New data table with inline editing
Takes ~15 min. Comments due Wednesday EOD.
Design Team""",
        "has_attachments": False, "thread_depth": 1, "word_count": 76,
        "ground_truth": {"category": "normal", "priority_score": 0.47,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["figma", "feedback", "design", "wednesday", "mockup", "review"]}
    },
    {
        "id": "e014",
        "subject": "Promotion approved — Senior Director, Engineering",
        "sender": "hr@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T14:00:00Z",
        "body": """Dear [Employee],
Your promotion to Senior Director, Engineering has been approved by the compensation committee.
Effective: February 1, 2024
New title: Senior Director, Engineering
Compensation adjustment: See attached letter (confidential)
Your manager will schedule formal announcement + 1:1 to discuss expanded responsibilities.
Congratulations on this achievement! — HR Team""",
        "has_attachments": True, "thread_depth": 0, "word_count": 61,
        "ground_truth": {"category": "internal", "priority_score": 0.58,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["thank", "promotion", "excited", "responsibilities", "honored"]}
    },
    {
        "id": "e015",
        "subject": "Q1 OKR planning — input needed from all team leads",
        "sender": "strategy@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:00:00Z",
        "body": """Hi team leads,
Q1 OKR planning cycle kicks off next week. Please submit your team's draft OKRs by Jan 19:
• 3–5 Objectives with measurable Key Results
• Link to H2 company priorities (growth, retention, platform stability)
• Stretch goal flagged separately
Template: notion.so/okr-template-q1-2024
Questions? Ping @strategy-team in Slack.
Due: January 19 (Friday) EOD""",
        "has_attachments": False, "thread_depth": 0, "word_count": 72,
        "ground_truth": {"category": "internal", "priority_score": 0.43,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["okr", "objectives", "submit", "friday", "team", "q1"]}
    },
    {
        "id": "e016",
        "subject": "Re: Enterprise renewal — Acme Corp (3yr deal, $240K ARR)",
        "sender": "sales@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T11:00:00Z",
        "body": """Hi,
Acme Corp 3-year renewal is at risk. Their procurement team wants:
1. 15% discount off list (we've been offering 10%)
2. SLA upgrade: 99.99% uptime (current contract: 99.9%)
3. Dedicated CSM assigned
Deal closes Jan 22 or they go with competitor. $240K ARR at stake.
Need your approval on discount and SLA terms.
— Marcus, Enterprise Sales""",
        "has_attachments": False, "thread_depth": 3, "word_count": 74,
        "ground_truth": {"category": "normal", "priority_score": 0.85,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["discount", "sla", "approve", "acme", "renewal", "240k", "csm"]}
    },
    {
        "id": "e017",
        "subject": "Candidate offer: Maya Patel — Staff Engineer (competing offer)",
        "sender": "recruiting@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T13:00:00Z",
        "body": """Hi,
Maya Patel (Staff Engineer candidate) has a competing offer expiring Friday.
Our offer: $195K base + $40K equity (4yr vest)
Competing offer: $210K base + $30K equity (Google)
Recommendation: Counter at $205K base + maintain equity.
Maya is a strong candidate — 8 YOE, Go/Rust, distributed systems.
Need your approval to counter by Thursday 5 PM.
Recruiting""",
        "has_attachments": False, "thread_depth": 1, "word_count": 71,
        "ground_truth": {"category": "normal", "priority_score": 0.78,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["approve", "counter", "maya", "offer", "205k", "salary", "thursday"]}
    },
    {
        "id": "e018",
        "subject": "Post-mortem: Jan 12 outage — action items assigned",
        "sender": "sre@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """Post-Mortem: Production Outage — Jan 12, 2024
Duration: 2h 14min  |  Impact: 23% users affected  |  Root cause: Redis memory exhaustion
Action items assigned to your team:
AI-001: Add Redis memory alerts (Owner: @backend, Due: Jan 19) — BLOCKED
AI-002: Implement circuit breaker pattern (Owner: @backend, Due: Jan 26)
AI-003: Runbook update (Owner: @sre, Due: Jan 22)
Please confirm AI-001 is unblocked or raise blocker.
SRE Team""",
        "has_attachments": True, "thread_depth": 2, "word_count": 78,
        "ground_truth": {"category": "normal", "priority_score": 0.66,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["ai-001", "redis", "blocker", "unblocked", "confirm", "action"]}
    },
    {
        "id": "e019",
        "subject": "Vendor: Cloudflare contract renewal — $36K, auto-renews Jan 20",
        "sender": "procurement@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:00:00Z",
        "body": """Heads up: Cloudflare annual contract auto-renews Jan 20 ($36,000).
Options:
A) Approve renewal as-is (no action needed — will auto-renew)
B) Negotiate: usage has dropped 30% — could renegotiate to $25K
C) Evaluate alternatives (Fastly, Akamai) — needs 30-day notice
Recommendation: B — renegotiate given usage drop.
Need decision by Jan 18 to allow negotiation time.
Procurement""",
        "has_attachments": False, "thread_depth": 0, "word_count": 74,
        "ground_truth": {"category": "normal", "priority_score": 0.68,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["cloudflare", "renegotiate", "renew", "decision", "jan 18", "contract"]}
    },
    {
        "id": "e020",
        "subject": "Re: Customer success — NPS dropped to 34 (from 67 last quarter)",
        "sender": "cs@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T11:45:00Z",
        "body": """NPS dropped 33 points this quarter — most critical issues from open responses:
1. Support response time: avg 4.2 days (SLA: 1 day) — 38% of negative responses
2. Missing features vs competitors: bulk export, SSO — 27%
3. Pricing perceived as high after recent 15% increase — 22%
Recommended: Emergency customer success review + rapid response team.
Need your sign-off on emergency budget: $15K.
CS Director""",
        "has_attachments": True, "thread_depth": 1, "word_count": 81,
        "ground_truth": {"category": "normal", "priority_score": 0.80,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["nps", "approve", "budget", "support", "response time", "customer"]}
    },

    # ── INTERNAL / LOW ACTION ──────────────────────────────────────────────────
    {
        "id": "e021",
        "subject": "Sprint 12 review notes + Sprint 13 planning Thursday 2PM",
        "sender": "pm@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """Sprint 12 outcomes:
• Velocity: 42 story points (target: 38) ✓
• 3 tickets carried to S13: auth refactor, notifications, batch export
• Demo: positive stakeholder feedback
Sprint 13 planning: Thursday 2PM. Please review backlog beforehand.
Retro actions: improve PR review turnaround, add monitoring to payment service.
Notes doc: notion.so/sprint12-notes""",
        "has_attachments": True, "thread_depth": 0, "word_count": 66,
        "ground_truth": {"category": "internal", "priority_score": 0.35,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e022",
        "subject": "All-hands Q1 kickoff — Jan 22 @ 9AM, RSVP by Jan 19",
        "sender": "calendar@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:00:00Z",
        "body": """Q1 All-Hands Kickoff | Monday Jan 22 | 9–11AM PST
Main Conference Room + Zoom: zoom.us/j/123456789
Agenda: CEO year in review (30), Department Q1 priorities (45), Q&A (30)
RSVP by Jan 19. Zoom link above. Optional coffee & networking after.
Please share with your team.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 55,
        "ground_truth": {"category": "internal", "priority_score": 0.28,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e023",
        "subject": "Slack outage — use email for urgent communications",
        "sender": "it@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T11:00:00Z",
        "body": """Slack experiencing outage (status.slack.com — Investigating).
ETA: 1-2 hours. Please use email for urgent comms.
P0 incidents: call on-call directly (company directory).
IT will send all-clear when Slack is restored.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 43,
        "ground_truth": {"category": "internal", "priority_score": 0.32,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e024",
        "subject": "Password expiry reminder — update by January 18",
        "sender": "it-security@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:00:00Z",
        "body": """Your company password expires in 3 days (January 18).
Update at: https://password.company.com
Requirements: 12+ chars, uppercase, lowercase, number, special char. Last 10 not reusable.
Questions: IT Help Desk ext. 1234.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 41,
        "ground_truth": {"category": "low", "priority_score": 0.18,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e025",
        "subject": "Team lunch this Friday — Nobu, 12:30PM — RSVP",
        "sender": "assistant@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:30:00Z",
        "body": """Team lunch this Friday at Nobu, 12:30 PM.
Celebrating Q4 wins! 🎉 Please RSVP by Thursday so we can confirm the reservation.
Reply with: Yes / No / Maybe. Dietary restrictions? Please note in reply.
— Executive Assistant""",
        "has_attachments": False, "thread_depth": 0, "word_count": 48,
        "ground_truth": {"category": "internal", "priority_score": 0.15,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e026",
        "subject": "Office kitchen reminder — label your food",
        "sender": "office-manager@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:00:00Z",
        "body": """Friendly reminder: Please label food in the office fridge with your name and date.
Fridge cleared every Friday 5PM — unlabeled items discarded.
Dishwasher runs nightly. Please clean up after yourself.
Thanks! — Office Management""",
        "has_attachments": False, "thread_depth": 0, "word_count": 44,
        "ground_truth": {"category": "low", "priority_score": 0.05,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e027",
        "subject": "Cafeteria menu this week",
        "sender": "cafeteria@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T07:30:00Z",
        "body": """This week's menu (11:30–2PM):
Mon: Grilled chicken + roasted veg | Tue: Pasta bar | Wed: Taco bar
Thu: Indian buffet | Fri: BBQ
Vegan/GF options daily. Pre-order via cafeteria app for priority pickup.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 46,
        "ground_truth": {"category": "low", "priority_score": 0.02,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e028",
        "subject": "Monthly wellness newsletter — January edition",
        "sender": "wellness@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T08:00:00Z",
        "body": """January Wellness Newsletter
This month: Mental health resources during Q1 crunch, meditation app subscription (free),
standing desk ergonomics guide, and Jan 24 wellness webinar: Managing Stress at Work.
EAP reminder: 24/7 counseling available — 1-800-EAP-HELP (confidential).""",
        "has_attachments": False, "thread_depth": 0, "word_count": 52,
        "ground_truth": {"category": "low", "priority_score": 0.08,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e029",
        "subject": "IT: Scheduled maintenance window — Sunday 2-4AM",
        "sender": "it@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T15:00:00Z",
        "body": """Scheduled maintenance: Sunday Jan 21, 2–4 AM PST.
Services affected: internal wiki, VPN, email (brief), dev environments.
Production services will NOT be affected. No action needed unless you have Sunday deploys planned.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 44,
        "ground_truth": {"category": "internal", "priority_score": 0.22,
            "requires_response": False, "correct_action": "archive"}
    },

    # ── SPAM / PHISHING ────────────────────────────────────────────────────────
    {
        "id": "e030",
        "subject": "🎉 Exclusive rewards — claim your $500 gift NOW!",
        "sender": "rewards@promo-deals-24.net", "sender_domain": "promo-deals-24.net",
        "timestamp": "2024-01-15T03:15:00Z",
        "body": """Congratulations! You've been SELECTED for our EXCLUSIVE Premium Rewards!
CLAIM $500 IN FREE GIFTS: http://totally-not-phishing.promo-deals-24.net/claim
Offer expires in 24 hours! Click NOW!""",
        "has_attachments": False, "thread_depth": 0, "word_count": 35,
        "ground_truth": {"category": "spam", "priority_score": 0.0,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e031",
        "subject": "FINAL NOTICE: Domain expiring — yourcompany.com",
        "sender": "billing@domains-r-us.biz", "sender_domain": "domains-r-us.biz",
        "timestamp": "2024-01-15T05:30:00Z",
        "body": """URGENT: Your domain expires in 7 days!
RENEW NOW for $89.99/year (normally $9.99 at your actual registrar)
Don't let your domain expire! renew-now.domains-r-us.biz""",
        "has_attachments": False, "thread_depth": 0, "word_count": 33,
        "ground_truth": {"category": "spam", "priority_score": 0.0,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e032",
        "subject": "Your account has been suspended — verify immediately",
        "sender": "noreply@paypa1-secure.com", "sender_domain": "paypa1-secure.com",
        "timestamp": "2024-01-15T04:00:00Z",
        "body": """IMPORTANT: Your PayPal account has been suspended due to unusual activity.
Verify your identity immediately: http://secure-paypa1-login.com/verify
Failure to verify within 24 hours will result in permanent account closure.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 38,
        "ground_truth": {"category": "spam", "priority_score": 0.0,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e033",
        "subject": "Investment opportunity — 340% returns guaranteed",
        "sender": "invest@crypto-returns-guaranteed.io", "sender_domain": "crypto-returns-guaranteed.io",
        "timestamp": "2024-01-15T02:00:00Z",
        "body": """GUARANTEED 340% returns on your investment in 30 days!
Our AI trading bot has never lost a trade. Minimum investment: $500.
Act now — only 12 spots left. Reply to secure your position!""",
        "has_attachments": False, "thread_depth": 0, "word_count": 36,
        "ground_truth": {"category": "spam", "priority_score": 0.0,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e034",
        "subject": "LinkedIn: 47 people viewed your profile this week",
        "sender": "notifications@linkedin.com", "sender_domain": "linkedin.com",
        "timestamp": "2024-01-15T06:00:00Z",
        "body": """47 people viewed your profile this week — up 23% from last week!
See who's looking: linkedin.com/in/yourprofile/viewers
Top companies: Google, Meta, Stripe. Upgrade to Premium to see all viewers.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 38,
        "ground_truth": {"category": "low", "priority_score": 0.04,
            "requires_response": False, "correct_action": "archive"}
    },
    {
        "id": "e035",
        "subject": "TechCrunch weekly digest — AI, funding, exits",
        "sender": "newsletter@techcrunch.com", "sender_domain": "techcrunch.com",
        "timestamp": "2024-01-15T06:00:00Z",
        "body": """TechCrunch Weekly — Jan 15, 2024
• OpenAI announces GPT-5 with 10x parameter increase
• Apple Vision Pro ships to first customers
• Stripe valuation cut 50% in secondary market
• EU AI Act passes final vote — enforcement 2026
• Y Combinator W24: 200 startups announced""",
        "has_attachments": False, "thread_depth": 0, "word_count": 52,
        "ground_truth": {"category": "low", "priority_score": 0.09,
            "requires_response": False, "correct_action": "archive"}
    },

    # ── EXTERNAL / PARTNER ─────────────────────────────────────────────────────
    {
        "id": "e036",
        "subject": "Re: Integration request — Zapier wants featured partner status",
        "sender": "partnerships@zapier.com", "sender_domain": "zapier.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """Hi,
Zapier would like to feature your product in our "Top 10 Integrations" campaign (8M users).
Requirements: native webhook support (you already have this), co-branded landing page, joint press release.
Timeline: Feature goes live Feb 1. Decision needed by Jan 19.
Revenue projection: ~$180K ARR from Zapier-sourced users (based on similar partners).
— Partnerships, Zapier""",
        "has_attachments": True, "thread_depth": 1, "word_count": 72,
        "ground_truth": {"category": "external", "priority_score": 0.71,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["zapier", "partner", "feature", "jan 19", "integration", "approve"]}
    },
    {
        "id": "e037",
        "subject": "Analyst briefing request — Gartner Magic Quadrant submission",
        "sender": "analyst-relations@gartner.com", "sender_domain": "gartner.com",
        "timestamp": "2024-01-15T09:00:00Z",
        "body": """Gartner Magic Quadrant — Enterprise Collaboration Tools — 2024 Edition
We are extending an invitation to participate in this year's Magic Quadrant.
Deadline for submission: February 15.
Requirements: 2-hour briefing (virtual), customer references (3+), product roadmap.
Inclusion in MQ typically drives 20-40% increase in inbound enterprise leads.
Please confirm participation by Jan 22.""",
        "has_attachments": True, "thread_depth": 0, "word_count": 70,
        "ground_truth": {"category": "external", "priority_score": 0.75,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["gartner", "magic quadrant", "participate", "confirm", "briefing", "feb 15"]}
    },
    {
        "id": "e038",
        "subject": "Press request — Forbes feature on AI-first companies",
        "sender": "reporter@forbes.com", "sender_domain": "forbes.com",
        "timestamp": "2024-01-15T11:30:00Z",
        "body": """Hi,
I'm writing a Forbes feature on 'Top 25 AI-First Companies to Watch in 2024.'
Your company has been shortlisted. I'd like a 20-min interview with your CEO or CPO.
Deadline: Story publishes Jan 30 — interview needed by Jan 24.
This is a high-visibility placement (forbes.com/tech, ~4M readers).
Please confirm availability. — Jessica Wu, Forbes Technology""",
        "has_attachments": False, "thread_depth": 0, "word_count": 72,
        "ground_truth": {"category": "external", "priority_score": 0.68,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["forbes", "interview", "ceo", "jan 24", "confirm", "availability"]}
    },
    {
        "id": "e039",
        "subject": "Customer success — Stripe expanding to 5,000 seats ($280K ARR)",
        "sender": "cs@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T14:00:00Z",
        "body": """Great news: Stripe wants to expand from 500 to 5,000 seats.
New contract value: $280,000 ARR (up from $28,000).
Requirements: dedicated CSM, 99.99% SLA, quarterly business reviews, SSO (SAML).
They need contract signed by Jan 31. Legal review started.
Need your approval on SLA upgrade and CSM allocation.
— CS Team""",
        "has_attachments": False, "thread_depth": 2, "word_count": 65,
        "ground_truth": {"category": "external", "priority_score": 0.89,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["stripe", "approve", "sla", "csm", "contract", "280k", "saml"]}
    },
    {
        "id": "e040",
        "subject": "Conference speaking slot — AWS re:Invent (45-min keynote)",
        "sender": "events@awsreinvent.com", "sender_domain": "awsreinvent.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """AWS re:Invent 2024 — Speaking Opportunity
We'd like to offer your CTO a 45-minute keynote slot at re:Invent (Las Vegas, Dec 2-6).
Expected audience: 15,000+ attendees. Topic: AI infrastructure at scale.
Benefits: Premier sponsor visibility, featured in AWS marketing, 10 complimentary passes.
Deadline to confirm: February 1. Please indicate interest and proposed topic.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 65,
        "ground_truth": {"category": "external", "priority_score": 0.60,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["aws", "reinvent", "keynote", "cto", "confirm", "speaking", "feb 1"]}
    },

    # ── ADDITIONAL RICH SET ────────────────────────────────────────────────────
    {
        "id": "e041",
        "subject": "CRITICAL: SSL certificate expires in 24h — prod.company.com",
        "sender": "monitoring@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """SSL Certificate Expiry Alert — CRITICAL
Domain: prod.company.com  |  Expires: Jan 16, 2024 10:00 UTC (24 hours from now)
If expired: All HTTPS connections will fail — browser security warnings for all users.
Auto-renewal FAILED (Let's Encrypt ACME challenge failure).
Manual renewal required immediately. DevOps ticket #DEV-8821 created.""",
        "has_attachments": False, "thread_depth": 0, "word_count": 55,
        "ground_truth": {"category": "urgent", "priority_score": 0.96,
            "requires_response": False, "correct_action": "escalate",
            "escalate_to": "devops"}
    },
    {
        "id": "e042",
        "subject": "Re: Layoff rumors — team morale at risk, need your statement",
        "sender": "hr@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T13:30:00Z",
        "body": """Hi,
Layoff rumors are spreading after the TechCrunch article this morning. Several engineers have
asked me directly if their jobs are safe. Team morale is visibly low.
Recommended: Brief all-hands statement from you today clarifying the company's position.
I can help draft the message — just need your guidance on what you can share.
— HR Director""",
        "has_attachments": False, "thread_depth": 0, "word_count": 72,
        "ground_truth": {"category": "urgent", "priority_score": 0.88,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["statement", "morale", "team", "clarify", "all-hands", "message"]}
    },
    {
        "id": "e043",
        "subject": "Re: Contractor invoice — $45,000 dispute with Accenture",
        "sender": "finance@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T09:45:00Z",
        "body": """Finance escalation: Accenture is disputing our non-payment of invoice #ACC-2024-003 ($45,000).
We dispute $28,000 of this (work not delivered per SOW §3.2).
Accenture's legal team has been engaged. Payment demand letter received today.
Our position: $17,000 payable (delivered work), $28,000 disputed.
Need your authorization to engage our legal team in response. Deadline: 5 business days.""",
        "has_attachments": True, "thread_depth": 2, "word_count": 77,
        "ground_truth": {"category": "urgent", "priority_score": 0.87,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["authorize", "legal", "accenture", "dispute", "invoice", "17000"]}
    },
    {
        "id": "e044",
        "subject": "Product feedback — enterprise customer threatening churn",
        "sender": "cs@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T14:30:00Z",
        "body": """At-risk account: Salesforce (Enterprise, $420K ARR).
CSM notes: Their VP Engineering says the API rate limits (1K req/min) are blocking their use case.
Competitor offer: Same price, 10K req/min.
Requested: Rate limit increase to 5K req/min for their account (custom tier).
Renewal date: March 1 — 45 days away. Churn risk: HIGH.
Need your decision on custom rate limit exception.""",
        "has_attachments": False, "thread_depth": 3, "word_count": 77,
        "ground_truth": {"category": "normal", "priority_score": 0.91,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["rate limit", "approve", "salesforce", "exception", "custom", "churn"]}
    },
    {
        "id": "e045",
        "subject": "Engineering: Tech debt sprint approval — 2-week freeze",
        "sender": "engineering@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "body": """Engineering team proposing a 2-week tech debt sprint (Feb 5-16).
Current tech debt score: 847 (critical threshold: 800). If unaddressed:
- Estimated 30% velocity reduction by Q2
- 3 critical security vulnerabilities remain unpatched
- Payment service reliability at risk
Trade-off: ~8 product features delayed by 2 weeks.
Need your approval to proceed with freeze.""",
        "has_attachments": False, "thread_depth": 1, "word_count": 67,
        "ground_truth": {"category": "normal", "priority_score": 0.73,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["approve", "tech debt", "sprint", "freeze", "security", "feb"]}
    },
    {
        "id": "e046",
        "subject": "Re: Marketing budget reallocation — $200K from events to paid",
        "sender": "marketing@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T11:00:00Z",
        "body": """Marketing Q1 proposal: Reallocate $200K from events budget to paid acquisition.
Rationale: Last 3 events generated 12 SQLs at $8,333 CAC. Paid search generating at $1,200 CAC.
Proposed split: $150K Google/LinkedIn paid, $50K content/SEO.
Projected impact: +120 SQLs this quarter (vs. 12 from events).
Need your approval before Feb 1 campaign launch. — CMO""",
        "has_attachments": True, "thread_depth": 1, "word_count": 73,
        "ground_truth": {"category": "normal", "priority_score": 0.65,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["approve", "marketing", "budget", "200k", "paid", "reallocate"]}
    },
    {
        "id": "e047",
        "subject": "Board deck review — slide 14 needs updated ARR chart",
        "sender": "ceo@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T16:00:00Z",
        "body": """Quick one — reviewing the board deck and slide 14's ARR chart shows $8.2M.
We closed the Stripe expansion deal last week making it $8.48M.
Can you update the chart and resend by 8 AM tomorrow? Board deck goes to print at 9 AM.
Also double-check slide 22 net revenue retention — should be 118%, not 112%.
Thanks — CEO""",
        "has_attachments": False, "thread_depth": 0, "word_count": 72,
        "ground_truth": {"category": "urgent", "priority_score": 0.93,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["arr", "update", "slide", "8.48", "board", "deck", "8 am"]}
    },
    {
        "id": "e048",
        "subject": "Re: ISO 27001 certification — audit scheduled Feb 20",
        "sender": "security@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T10:30:00Z",
        "body": """ISO 27001 certification audit scheduled Feb 20-21 (Deloitte auditors).
Pre-audit checklist items requiring your sign-off:
1. Information Security Policy (last updated 2021 — needs review)
2. Risk register updated for 2024 threats
3. Vendor assessment for 12 new vendors onboarded this year
4. Access control review for all admin users
5. Incident response plan updated post-Jan 12 outage
Lead time: 3 weeks. Start by Jan 25 at latest.""",
        "has_attachments": True, "thread_depth": 1, "word_count": 83,
        "ground_truth": {"category": "normal", "priority_score": 0.77,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["iso", "audit", "sign-off", "security policy", "jan 25", "review"]}
    },
    {
        "id": "e049",
        "subject": "Acquisition interest — Series B startup wants acquisition talk",
        "sender": "corp-dev@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T12:00:00Z",
        "body": """Corp Dev update: Received inbound from Meshify (Series B, $12M ARR, 45-person team).
They build infrastructure monitoring — complementary to our platform.
Founder reached out via LinkedIn — wants to explore acquisition.
Last round valuation: $60M. Estimated acquisition range: $45-65M.
Should we pursue a preliminary call? I'd need your go/no-go to proceed.
— Corp Dev Lead""",
        "has_attachments": False, "thread_depth": 0, "word_count": 74,
        "ground_truth": {"category": "normal", "priority_score": 0.70,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["acquisition", "meshify", "pursue", "call", "go", "proceed"]}
    },
    {
        "id": "e050",
        "subject": "Re: Engineering offsite — budget approval needed ($85K)",
        "sender": "engineering@company.com", "sender_domain": "company.com",
        "timestamp": "2024-01-15T11:30:00Z",
        "body": """Engineering offsite proposal:
Dates: March 18-20 (Mon-Wed), Napa Valley
Budget: $85,000 (travel $35K, venue $30K, activities $20K)
Attendees: 62 engineers + 8 team leads
Objectives: Q2 roadmap alignment, cross-team relationship building, hackathon
Previous offsite ROI: 23% velocity increase in 6 weeks after last event.
Need budget approval by Jan 22 to book venue.
— VP Engineering""",
        "has_attachments": True, "thread_depth": 0, "word_count": 77,
        "ground_truth": {"category": "normal", "priority_score": 0.55,
            "requires_response": True, "correct_action": "respond",
            "response_keywords": ["approve", "offsite", "budget", "85k", "march", "engineering"]}
    },
]

# ── Lookup helpers ─────────────────────────────────────────────────────────────
EMAIL_BY_ID: dict[str, dict] = {e["id"]: e for e in EMAILS}

# Task email sets
TASK_1_EMAILS = [e["id"] for e in EMAILS[:20]]          # First 20
TASK_2_EMAILS = [e["id"] for e in EMAILS                # All that need responses
                 if e["ground_truth"]["requires_response"]][:15]
TASK_3_EMAILS = [e["id"] for e in EMAILS]               # All 50

# Category breakdown for reference
CATEGORY_COUNTS = {}
for e in EMAILS:
    cat = e["ground_truth"]["category"]
    CATEGORY_COUNTS[cat] = CATEGORY_COUNTS.get(cat, 0) + 1
