from __future__ import annotations
from app.data import EMAIL_BY_ID, TASK_2_EMAILS

MAX_ACT=0.20; MAX_KW=0.40; MAX_COMP=0.20; MAX_TONE=0.20

# Comprehensive synonym groups — any hit in any group counts
SYNONYMS: dict[str, list[list[str]]] = {
    # respond emails
    "e002": [["budget","headcount","capex","numbers","figures","financials","data"],
             ["9:45","9:30","am","morning","board","presentation","by"],
             ["sending","attached","here","ready","available","coming","have"],
             ["sorry","apologize","delay","late","apologies","heads up","pardon"]],
    "e004": [["authorize","authorized","approved","proceed","go ahead","permission","sanction"],
             ["gdpr","breach","notification","notification letters","compliance","72","data breach"],
             ["password","reset","accounts","affected","force","mandatory","credentials"],
             ["immediately","now","urgent","without delay","asap","priority","right away"]],
    "e005": [["reject","decline","not acceptable","remove","against","refuse","no to"],
             ["9.1","clause 9","unlimited liability","liability","data breach clause"],
             ["11.3","clause 11","ip","derivative","intellectual property","works"],
             ["proceed","counter","negotiate","acme","contract","sign","today","deadline"]],
    "e007": [["hipaa","audit","compliance","findings","deloitte","violations"],
             ["response","plan","remediation","address","fix","resolve","submit"],
             ["48","hours","deadline","by","within","respond","time"],
             ["encrypt","access log","baa","vendor","phi","high severity","retention"]],
    "e009": [["refund","reimburse","credit","money back","reimbursement","repay"],
             ["apologize","sorry","apologies","regret","inconvenience","understand","empathize"],
             ["approved","approve","process","issue","authorize","granted","confirmed"],
             ["jane","customer","premium","valued","order","ord-88234","3 year"]],
    "e010": [["proposal","partnership","integration","agreement","datasync","deal"],
             ["review","reviewed","read","evaluate","look through","consider","assessed"],
             ["schedule","follow-up","follow up","call","meeting","discuss","connect","week"],
             ["alex","partner","revenue share","co-marketing","integration","available"]],
    "e011": [["alex","thompson","onboarding","new hire","monday","start","jan 22"],
             ["laptop","provisioned","slack","github","jira","access","it ticket","5891"],
             ["1:1","schedule","monday","10 am","meeting","confirmed","arranged","ready"],
             ["complete","done","checklist","confirmed","friday","eod","finished"]],
    "e012": [["invoice","inv-2024-891","billing","charge","dispute","discrepancy"],
             ["investigate","resolve","correct","adjust","credit","fix","review","apologize"],
             ["seats","discount","20%","enterprise","ent-2021","contract","jennifer"],
             ["24 hours","24h","priority","resolve","asap","respond","business days"]],
    "e013": [["figma","mockup","design","v2","interface","ui","ux","redesign"],
             ["feedback","review","comments","input","thoughts","notes","response"],
             ["wednesday","wed","eod","by","deadline","thursday","before","end of day"],
             ["navigation","nav","mobile","responsive","color","palette","sidebar","top nav"]],
    "e014": [["thank","congratulations","grateful","honored","excited","thrilled","appreciate","wonderful"],
             ["promotion","senior director","role","position","title","opportunity","achievement"],
             ["responsibilities","team","expanded","forward","look forward","ready","eager"],
             ["february","feb","effective","announcement","manager","discuss","february 1"]],
    "e015": [["okr","objectives","key results","goals","targets","planning"],
             ["submit","submission","send","provide","deliver","share","draft"],
             ["friday","jan 19","january 19","eod","deadline","by","before"],
             ["q1","quarter","team","growth","retention","platform","priorities"]],
    "e016": [["approve","approved","discount","15%","terms","pricing","accept","agree"],
             ["sla","uptime","99.99","service level","reliability","guarantee"],
             ["csm","customer success","dedicated","manager","support","assign"],
             ["acme","renewal","deal","240k","jan 22","january","deadline","close"]],
    # escalate emails — graded on escalate action + reason quality
    "e003": [["escalate","security","team","tor","breach","risk","compromise","account"],
             ["2fa","bypass","login","unauthorized","suspicious","ip","tor exit"],
             ["investigate","review","lock","secure","urgent","immediate","action"],
             ["security team","soc","infosec","it security","report","incident"]],
    "e006": [["payment","gateway","stripe","down","failing","outage","revenue"],
             ["authorize","authorization","approve","engineering","vendor","escalate"],
             ["emergency","critical","urgent","immediately","$47","47000","revenue loss"],
             ["engineering lead","ops","devops","on-call","team","rollback","fix"]],
    "e008": [["aws","lambda","billing","84000","unexpected","runaway","cloud"],
             ["escalate","cloud ops","devops","investigate","remediate","fix","review"],
             ["rate limit","disable","stop","loop","invocation","eu-west","function"],
             ["emergency","critical","urgent","account","prod","production","immediately"]],
}

class ResponseTask:
    task_id="task_2"; name="Response Drafting"; difficulty="medium"
    description=("Draft professional responses to 15 emails requiring replies or escalations. "
                 "Graded on: action correctness, keyword/topic coverage, response completeness, tone quality. "
                 "Urgent emails need urgency language and decisive action. "
                 "Escalation emails need clear escalation target and reason. "
                 "Goal: Responses that fully satisfy the original sender.")
    max_steps=25; pass_threshold=0.78

    def __init__(self):
        self.emails=[EMAIL_BY_ID[i] for i in TASK_2_EMAILS]

    def get_emails(self): return self.emails

    def grade_response(self, action, email):
        gt=email["ground_truth"]; eid=email["id"]; c={}
        at=action.get("action_type",""); ca=gt["correct_action"]
        if at in ("archive","skip"):
            return {"total":0.0,"components":{"action_type":0.0}}
        # Action type (20%)
        if at in ("respond","compose") and ca in ("respond","compose"):   c["action_type"]=0.20
        elif at in ("escalate","flag") and ca in ("escalate","flag"):      c["action_type"]=0.20
        elif at in ("respond","compose") and ca=="escalate":               c["action_type"]=0.12  # partial: right family
        elif at in ("escalate","flag") and ca=="respond":                  c["action_type"]=0.12
        elif at in ("respond","compose","escalate","flag","triage"):       c["action_type"]=0.08
        else:                                                               c["action_type"]=0.0
        txt=(action.get("response_text") or action.get("reason") or "").lower()
        # Keyword coverage (40%) — synonym-aware, includes escalate_to for escalate actions
        if at=="escalate":
            eto=(action.get("escalate_to") or "").lower()
            txt=txt+" "+eto
        groups=SYNONYMS.get(eid,[])
        if groups:
            hits=sum(1 for g in groups if any(s in txt for s in g))
            c["keyword_coverage"]=round(0.40*(hits/len(groups)),4)
        else:
            kws=gt.get("response_keywords",[])
            c["keyword_coverage"]=round(0.40*(sum(1 for k in kws if k.lower() in txt)/max(len(kws),1)),4) if kws else 0.30
        # Completeness (20%) — lower bar for escalate (reason can be brief)
        wc=len(txt.split())
        if ca=="escalate":
            c["completeness"]=0.20 if wc>=10 else 0.15 if wc>=5 else 0.08 if wc>=2 else 0.0
        else:
            c["completeness"]=0.20 if wc>=25 else 0.15 if wc>=12 else 0.08 if wc>=6 else 0.03 if wc>=2 else 0.0
        # Tone (20%)
        c["tone"]=_tone(txt, gt["priority_score"])
        return {"total":round(min(1.0,sum(c.values())),4),"components":c}

    def compute_episode_score(self, graded):
        if not graded: return {"score":0.0,"breakdown":{}}
        n=len(graded); tot=len(self.emails)
        q=sum(g["total"] for g in graded)/n; cov=n/tot
        score=q*(0.70+0.30*cov)
        bd={
            "avg_action_correctness": round(sum(g["components"].get("action_type",0) for g in graded)/n/MAX_ACT,4),
            "avg_keyword_coverage":   round(sum(g["components"].get("keyword_coverage",0) for g in graded)/n/MAX_KW,4),
            "avg_completeness":       round(sum(g["components"].get("completeness",0) for g in graded)/n/MAX_COMP,4),
            "avg_tone":               round(sum(g["components"].get("tone",0) for g in graded)/n/MAX_TONE,4),
            "coverage":               round(cov,4),
            "quality_score":          round(q,4),
            "final_score":            round(score,4),
        }
        return {"score":round(score,4),"breakdown":bd}


def _tone(txt, pri):
    s=0.0
    # Broad opener recognition — action-oriented business language counts
    openers = [
        "thank you","thanks","hi ","hello","dear ",
        "i have","i will","i'll","i hereby","we have",
        "pleased","happy to","i've","confirmed","noted","acknowledged","understood",
        "i authorize","i approve","approved","approving","proceeding","escalating",
        "reject","rejecting","reviewed","reviewing","apologize","apologies","sorry",
        "investigating","confirmed","submitting","sending","attaching","updating",
        "authorizing","scheduling","allocating","accepting","declining","proceeding",
        "addressing","escalate","will have","will send","will provide","will resolve",
    ]
    if any(o in txt for o in openers): s+=0.08

    urg = ["immediately","urgent","asap","right away","without delay","promptly",
           "now","today","critical","priority","emergency","action required",
           "escalate","at once","straightaway","deadline","before","by "]
    neutral_action = ["will","approve","resolve","address","fix","complete","submit",
                      "confirm","arrange","provide","send","schedule","close","proceed"]

    if pri>=0.85:
        # High priority: urgency OR decisive action language scores full
        if any(u in txt for u in urg) or any(n in txt for n in neutral_action):
            s+=0.06
        else:
            s+=0.02
    elif pri>=0.50:
        s+=0.05  # medium: any professional response is fine
    else:
        s+=0.06 if not any(u in txt for u in urg) else 0.02  # low: avoid urgency

    # Closer OR action commitment
    closers = ["regards","sincerely","best","thanks","thank you","looking forward",
               "let me know","please let","feel free","reach out","happy to help",
               "do not hesitate","will follow","please confirm","best regards",
               "kind regards","yours","cheers","talk soon"]
    action_commit = ["will resolve","will send","will provide","will submit","will deliver",
                     "will confirm","will schedule","will arrange","will action",
                     "by eod","by friday","by tomorrow","by jan","by feb","before the"]
    if any(c in txt for c in closers) or any(a in txt for a in action_commit):
        s+=0.06

    return round(min(s,0.20),4)
