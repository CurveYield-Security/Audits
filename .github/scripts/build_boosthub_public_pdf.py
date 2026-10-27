"""Render the sealed Boosthub security audit from previously public aggregate evidence.

Release policy: one PDF per folder; seven public evidence references; no source ZIP.
No access to the private Audit-Controller repository, and no external PDF dependency.
"""
from pathlib import Path
import json
import math
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

ROOT = Path(__file__).resolve().parents[2]
FOLDER = "Boosthub Staking v2 - Linked Public Release"
DEST = ROOT / FOLDER
OUT = DEST / "CurveYield_Boosthub_Staking_v2_Linked_Security_Audit.pdf"
DEST.mkdir(parents=True, exist_ok=True)
scope = json.loads((DEST / "Audit_Scope.json").read_text(encoding="utf-8"))
registry = json.loads((DEST / "Findings_and_Remediation.json").read_text(encoding="utf-8"))
method = json.loads((DEST / "Methodology_and_Analysis.json").read_text(encoding="utf-8"))
execution = json.loads((DEST / "Execution_Results.json").read_text(encoding="utf-8"))
index = json.loads((DEST / "Evidence_Index.json").read_text(encoding="utf-8"))
findings = registry["findings"]
reports = {x["report"]: x["summary"] for x in method["methodology"]}
assert len(scope["scope"]) == 8 and len(findings) == 7
assert sum(x["status"] == "REMEDIATED_VERIFIED" for x in findings) == 4
assert sum(x["status"] == "ACCEPTED" for x in findings) == 3
assert all(x["severity"].lower() == "low" for x in findings)
assert len(index["evidence"]) == 6
assert len(execution["results"]) == 5
all_analysis = "\n".join(reports.values())
for token in ("26 positive executable requirements", "22 negative requirements", "28 invariants", "114/114"):
    assert token in all_analysis, f"Missing audit grounding for statistic: {token}"

links = [
    ("Audit scope", "Contracts, interfaces and admitted review boundaries", "Audit_Scope.json"),
    ("Findings and remediation", "Seven validated findings and their final outcomes", "Findings_and_Remediation.json"),
    ("Methodology and analysis", "Aggregated security assessment and technical work", "Methodology_and_Analysis.json"),
    ("Evidence index", "Selected public evidence and file integrity references", "Evidence_Index.json"),
    ("Execution results", "Adversarial reproductions and deterministic outcomes", "Execution_Results.json"),
    ("Medusa fuzz results", "Fuzzing terminal evidence", "Medusa_Fuzz_Results.json"),
    ("Native fuzz results", "Additional native fuzzing evidence", "Native_Fuzz_Results.json")
]
for _,_,name in links:
    assert (DEST/name).exists(),f"Missing publication-selected file {name}"
URL = "https://github.com/CurveYield-Security/Audits/blob/main/" + FOLDER.replace(" ","%20") + "/"

NAVY=HexColor("#0B1626")
DEEP=HexColor("#172338")
INK=HexColor("#0B1626")
MUTED=HexColor("#68717F")
TEAL=HexColor("#A36C00")
PALE=HexColor("#FFF5DD")
BLUE=HexColor("#D99100")
GOLD=HexColor("#F5B31A")
BORDER=HexColor("#EADDBF")
PANEL=HexColor("#FFFAF0")
WHITE=HexColor("#FFFFFF")
CREAM=HexColor("#FFFDF8")
# Semantic colors are reserved for issue severity, not for the core brand.
# They remain distinct from disposition colors (FIXED vs ACCEPTED).
SEVERITY_COLORS = {
    "critical": HexColor("#BF2942"),    # Crimson
    "high": HexColor("#D85D31"),        # Vermilion
    "medium": HexColor("#B47A13"),      # Amber
    "low": HexColor("#3269AE"),         # Sapphire
    "informational": HexColor("#765BA1") # Amethyst
}
SEVERITY_TINTS = {
    "critical": HexColor("#FFF0F2"),
    "high": HexColor("#FFF2EB"),
    "medium": HexColor("#FFF7E6"),
    "low": HexColor("#EFF5FD"),
    "informational": HexColor("#F5F0FC")
}
FIXED_COLOR = HexColor("#177B65")       # Status only: fixed and independently verified
FIXED_TINT = HexColor("#E8F5EF")
ACCEPTED_COLOR = HexColor("#9B640C")    # Status only: accepted, not remediated
ACCEPTED_TINT = HexColor("#FFF3DB")
# Brand tokens from saved CurveYield homepage CSS (v20/v21): ivory, ink and gold.
# Contrast-adjusted gold #A36C00 is used for small linked labels on light backgrounds.
H,W=A4[1],A4[0]

c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
page_no=0

def rect(x,y,w,h,fill,stroke=None,radius=0):
    c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke)
    if radius:
        c.roundRect(x,y,w,h,radius,stroke=int(stroke is not None),fill=1)
    else: c.rect(x,y,w,h,stroke=int(stroke is not None),fill=1)

def words(t,size=9,font="Helvetica",width=480):
    t=re.sub(r"[*`#]", "", str(t)).strip()
    return simpleSplit(t,font,size,width)

def para(t,x,top,width,size=9,color=INK,leading=13,max_lines=None,bold=False):
    font="Helvetica-Bold" if bold else "Helvetica"
    lines=words(t,size,font,width)
    if max_lines is not None:
        lines=lines[:max_lines]
    c.setFillColor(color);c.setFont(font,size)
    for i,line in enumerate(lines):
        c.drawString(x,top-i*leading,line)
    return top-max(1,len(lines))*leading

def start(title,section):
    global page_no
    page_no+=1
    rect(0,0,W,H,CREAM)
    rect(0,H-49,W,49,NAVY)
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",9)
    c.drawString(34,H-30,"CURVEYIELD  /  SECURITY AUDIT")
    c.setFont("Helvetica",8)
    c.drawRightString(W-34,H-30,section.upper())
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",19)
    c.drawString(35,H-87,title)
    c.setStrokeColor(BORDER);c.line(35,49,W-35,49)
    c.setFillColor(MUTED);c.setFont("Helvetica",7.5)
    c.drawString(35,34,"BOOSTHUB STAKING V2   /   SMART-CONTRACT SECURITY")
    c.drawRightString(W-35,34,f"{page_no:02}")
    return H-106

def end(): c.showPage()

def link_area(x,y,width,height,document):
    """Click the actual content region, not a separate evidence button."""
    assert document in {item[2] for item in links}, document
    c.linkURL(URL + document, (x,y,x+width,y+height), relative=0, thickness=0)

def linked_label(label,x,y,document,size=9,font="Helvetica-Bold",color=TEAL):
    """Write a real underlined hyperlink on the named information."""
    c.setFillColor(color)
    c.setFont(font,size)
    c.drawString(x,y,label)
    width=c.stringWidth(label,font,size)
    c.setStrokeColor(color)
    c.setLineWidth(.58)
    c.line(x,y-2,x+width,y-2)
    link_area(x,y-4,width,13,document)


# 01 COVER — editorial hero, no duplicated process housekeeping.
page_no+=1
rect(0,0,W,H,CREAM)
rect(0,H-21,W,21,GOLD)
rect(39,515,5,153,GOLD)
c.setFillColor(NAVY);c.setFont("Helvetica-Bold",11)
c.drawString(56,727,"CURVEYIELD  /  SMART-CONTRACT SECURITY")
c.setFont("Helvetica-Bold",32)
c.drawString(56,633,"BOOSTHUB")
c.drawString(56,593,"STAKING V2")
c.setFillColor(MUTED);c.setFont("Helvetica",13)
c.drawString(56,548,"Independent-review process  /  Sealed August 23, 2026")
rect(54,368,487,125,DEEP,radius=10)
link_area(54,368,487,125,"Findings_and_Remediation.json")
c.setFillColor(HexColor("#F5B31A"));c.setFont("Helvetica-Bold",10)
c.drawString(75,469,"FINAL SECURITY VERDICT")
c.setFillColor(WHITE);c.setFont("Helvetica-Bold",41)
c.drawString(74,409,"PASS")
c.setFont("Helvetica",11)
c.drawString(212,428,"Seven validated Low-severity findings")
c.drawString(212,407,"Four verified fixes  /  Three accepted residual risks")
rect(54,184,153,119,DEEP,radius=10)
rect(218,184,153,119,DEEP,radius=10)
rect(382,184,159,119,DEEP,radius=10)
for x,n,label in [(75,"8","SOURCE FILES REVIEWED"),(238,"114","ENTRYPOINTS REVIEWED"),(400,"0","MEDIUM / HIGH / CRITICAL")]:
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",24);c.drawString(x,239,n)
    c.setFillColor(HexColor("#FFE6A1"));c.setFont("Helvetica",7.5);c.drawString(x,210,label)
    if x==75: link_area(54,184,153,119,"Audit_Scope.json")
    elif x==238: link_area(218,184,153,119,"Methodology_and_Analysis.json")
    else: link_area(382,184,159,119,"Findings_and_Remediation.json")
c.setFillColor(MUTED);c.setFont("Helvetica",8)
c.drawString(56,110,"Scope: audited smart contracts only. No production deployment attestation is claimed.")
c.drawString(56,91,"This release links seven selected public evidence files; the source ZIP is not published.")
c.setFont("Helvetica",7.5);c.drawRightString(541,48,"01")
end()

# 02 EXECUTIVE ASSESSMENT — system purpose first, findings and repairs second
top=start("Executive summary","Executive")
c.setFillColor(TEAL);c.setFont("Helvetica-Bold",9.2)
c.drawString(35,top-7,"THE CONTRACT SYSTEM AND WHAT IT DOES")
para("This five-contract suite connects a depositor-facing Vault to a staking Strategy, a Vyper staking layer and the external BoostHub system. It handles principal, withdrawals, reward accrual and conversion for sdCRV, sdFXN and sdYB pool configurations. A governance token controls bounded incentive issuance.",35,top-28,516,9.1,MUTED,13,3)
top-=83
contract_rows=[
("CurveYieldVault","Holds depositor-facing share accounting and redemption claims. Its share pricing can include the Strategy's estimate of unharvested rewards."),
("CurveYieldStakingStrategyV2","Moves Vault assets into staking, orchestrates harvest and reward conversion, and controls specified rescue and ChildGauge pathways."),
("BoostHubStaking v17","Vyper staking adapter between the Strategy and BoostHub, handling stake state, reward distribution, fees and withdrawal timing."),
("SdYbRewardConverter","Implements sdYB-oriented conversion quotes and execution through external liquidity routes used in reward accounting."),
("CurveYieldGovernanceToken","Manages cyGOV supply, bounded minter allocations, owner privileges and transfer restrictions for governance incentives.")
]
for i,(name,description) in enumerate(contract_rows):
    y=top-57
    rect(35,y,525,56,PALE if i%2==0 else PANEL,stroke=BORDER,radius=6)
    label_size=8.9 if c.stringWidth(name,"Helvetica-Bold",8.9)<177 else 8.1
    linked_label(name,47,y+33,"Methodology_and_Analysis.json",size=label_size)
    para(description,222,y+38,326,8.5,INK,10.8,3)
    link_area(35,y,525,56,"Methodology_and_Analysis.json")
    top-=64

top-=9
c.setFillColor(TEAL);c.setFont("Helvetica-Bold",9.2)
c.drawString(35,top,"FINDINGS, REPAIRS AND WHAT REMAINS")
para("Seven Low-severity findings were validated. Four vulnerabilities were repaired and independently re-tested; three bounded, Low-severity economic risks remain expressly accepted. No Critical, High or Medium findings were validated.",35,top-20,518,9.0,MUTED,12.5,3)
rect(35,112,258,123,PALE,stroke=BORDER,radius=8)
rect(302,112,258,123,HexColor("#FFF5DD"),stroke=BORDER,radius=8)
linked_label("4 FIXED / VERIFIED",49,215,"Findings_and_Remediation.json",size=10,color=TEAL)
para("Converter pricing and executable tolerance were corrected; the stale reward-rescue timer was reset on reactivation; and sdYB WANT/native reward classification was repaired.",49,195,229,8.7,INK,12.5,5)
linked_label("3 ACCEPTED LOW RISKS",315,215,"Findings_and_Remediation.json",size=10,color=HexColor("#986000"))
para("The remaining risks involve marginal reward-preview effects on share issuance, privileged rescue of disabled reward balances, and reward carry stranded after disablement.",315,195,229,8.7,INK,12.5,5)
link_area(35,112,258,123,"Findings_and_Remediation.json")
link_area(302,112,258,123,"Findings_and_Remediation.json")
linked_label("Smart-contract scope and exclusions",35,80,"Audit_Scope.json",size=8.0,font="Helvetica")
linked_label("Public evidence provenance",313,80,"Evidence_Index.json",size=8.0,font="Helvetica")
end()
def metric_grid_page(title,section,groups):
    top=start(title,section)
    for group_title, entries in groups:
        c.setFillColor(TEAL);c.setFont("Helvetica-Bold",9.2)
        c.drawString(35,top-5,group_title.upper())
        top-=20
        cols=4;cw=126;ch=78;gap=7
        for i,(value,label) in enumerate(entries):
            col=i%cols;row=i//cols
            x=35+col*(cw+gap);y=top-ch-row*(ch+8)
            rect(x,y,cw,ch,PANEL,stroke=BORDER,radius=7)
            c.setFillColor(NAVY);c.setFont("Helvetica-Bold",24)
            c.drawString(x+12,y+44,str(value))
            para(label,x+12,y+28,cw-20,7.9,MUTED,10,2)
            # The statistic tile itself is linked to the most relevant public evidence.
            document=stat_source(label)
            c.setStrokeColor(TEAL);c.setLineWidth(1.5)
            c.line(x+12,y+9,x+29,y+9)
            link_area(x,y,cw,ch,document)
        top-=math.ceil(len(entries)/cols)*(ch+8)+27
    end()

def stat_source(label):
    # Every published statistic is bound to one of the seven selected aggregate records.
    if label in ("Implementations reviewed","Interfaces examined","Audited source files","Source languages"):
        return "Audit_Scope.json"
    if label in ("Substantive candidates","Candidates dispositioned","Dismissed candidates","Inconclusive candidates",
                 "Validated security findings","Verified remediations","Accepted residual findings"):
        return "Findings_and_Remediation.json"
    if label in ("Dynamically evidenced candidates",):
        return "Execution_Results.json"
    return "Methodology_and_Analysis.json"


# 03 UNIVERSAL AUDIT FOOTPRINT
metric_grid_page("Audit footprint","Universal statistics",[
("Codebase",[(5,"Implementations reviewed"),(3,"Interfaces examined"),(8,"Audited source files"),(2,"Source languages"),(114,"Reviewed entrypoints"),(9,"Authority actor categories"),(7,"Protected capital classes"),(6,"Documented trust boundaries")]),
("Architecture and scope",[(17,"Mapped asset-flow edges"),(10,"Assessed security domains"),(6,"Applicable security domains"),(1,"External staking platform"),(0,"Cross-chain domains"),(0,"Upgrade-proxy domains"),(0,"Lending domains"),(0,"Signature-specific domains")])
])

# 04 UNIVERSAL INVESTIGATION DEPTH
metric_grid_page("Depth of security investigation","Universal statistics",[
("Threat analysis",[(26,"Positive security requirements"),(22,"Negative security requirements"),(28,"Specified invariants"),(10,"Modeled threat scenarios"),(23,"Attack-tree branches"),(7,"Critical invariant families"),(130,"Neutral Slither observations"),(114,"Entrypoints manually reviewed")]),
("Validation and execution",[(9,"Substantive candidates"),(9,"Candidates dispositioned"),(2,"Dismissed candidates"),(0,"Inconclusive candidates"),(6,"Dynamically evidenced candidates"),(7,"Validated security findings"),(4,"Verified remediations"),(3,"Accepted residual findings")])
])

# 05 SECURITY FINDING RESULTS
top=start("Findings and resolution","Security outcomes")
rect(35,top-120,525,112,DEEP,radius=9)
c.setFillColor(SEVERITY_COLORS["low"]);c.setFont("Helvetica-Bold",28);c.drawString(51,top-55,"7 LOW")
link_area(35,top-120,525,112,"Findings_and_Remediation.json")
c.setFont("Helvetica",11);c.setFillColor(HexColor("#FFF5DD"))
c.drawString(51,top-85,"No validated Critical, High or Medium findings")
rect(292,top-101,116,67,HexColor("#293447"),radius=6)
rect(422,top-101,116,67,HexColor("#293447"),radius=6)
for x,num,lbl in [(306,"4","FIXED / VERIFIED"),(435,"3","ACCEPTED LOW")]:
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",22);c.drawString(x,top-72,num)
    c.setFont("Helvetica",7);c.drawString(x,top-89,lbl)
top-=157
c.setFillColor(NAVY);c.setFont("Helvetica-Bold",11);c.drawString(35,top,"VALIDATED FINDING SEVERITY")
top-=27
# Even when a class has zero findings, its distinct semantic hue is shown.
# The filled bar still communicates quantity; a colored chip communicates class.
for label,val,key in [("Critical",0,"critical"),("High",0,"high"),("Medium",0,"medium"),
                      ("Low",7,"low"),("Info",0,"informational")]:
    color = SEVERITY_COLORS[key]
    rect(36,top-4,7,17,color,radius=2)
    c.setFont("Helvetica-Bold",9);c.setFillColor(INK);c.drawString(49,top,label)
    rect(111,top-2,405,11,PANEL,radius=4)
    if val:
        rect(111,top-2,405*val/7,11,color,radius=4)
    c.setFillColor(color);c.setFont("Helvetica-Bold",10)
    c.drawRightString(550,top,str(val))
    link_area(35,top-8,525,23,"Findings_and_Remediation.json")
    top-=39
top-=8
c.setFillColor(NAVY);c.setFont("Helvetica-Bold",11);c.drawString(35,top,"CANDIDATE DISPOSITION")
top-=26
for label,num in [("Promoted to validated findings",7),("Dismissed after assessment",2),("Remaining inconclusive",0)]:
    rect(35,top-22,525,32,PANEL,radius=4)
    c.setFont("Helvetica",9);c.setFillColor(INK);c.drawString(47,top-11,label)
    c.setFont("Helvetica-Bold",12);c.drawRightString(544,top-12,str(num))
    top-=44
end()

# 06 TOPOLOGY AND TRUST
top=start("System architecture and trust","Technical analysis")
c.setFillColor(MUTED);c.setFont("Helvetica",9)
c.drawString(35,top-4,"Canonical principal-flow model; arrows describe accepted high-level interactions.")
top-=45
nodes=[("DEPOSITOR",42),("VAULT",150),("STRATEGY",262),("STAKING",374),("BOOSTHUB",472)]
for label,x in nodes:
    width=100 if label!="BOOSTHUB" else 92
    rect(x,top-57,width,55,PALE,stroke=BORDER,radius=7)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",8)
    c.drawCentredString(x+width/2,top-30,label)
    link_area(x,top-57,width,55,"Methodology_and_Analysis.json")
for x1,x2 in [(143,149),(250,260),(362,372),(474,471)]:
    c.setStrokeColor(TEAL);c.setLineWidth(1.5);c.line(x1,top-30,x2,top-30)
top-=112
for title,desc in [
("Principal and shareholder accounting","Deposits and redemptions flow through the Vault and Strategy; the staking system manages withdrawal queues and reward liability."),
("Reward conversion and price sensitivity","External Curve-style liquidity and quote paths affect reward conversion and estimated unharvested values. The remediated converter enforces oracle-aware tolerance."),
("Privileged control boundaries","Token minting, fee and reward configuration, rescue delays, and staking configuration are controlled by distinct authority roles."),
("Independent external dependencies","BoostHub, ERC-20 assets, reward converters, Curve pools and ChildGauge integrations introduce external liveness or trust assumptions.")
]:
    c.setFillColor(TEAL);c.setFont("Helvetica-Bold",11);c.drawString(35,top,title)
    before=top
    top=para(desc,35,top-18,522,9.2,MUTED,13,3)-31
    link_area(35,top+21,522,before-top-12,"Methodology_and_Analysis.json")
end()

# 07 EVIDENCE & TESTS
top=start("Adversarial verification","Technical evidence")
for n,title,desc in [
("01","Medusa fuzzing","The recorded Medusa terminal campaign tested source-bound security behavior and produced a decisive candidate reproduction."),
("02","Native fuzz execution","Foundry native fuzzing was invoked after Medusa; the recorded 10,000-run requested budget found a counterexample to the deposit property."),
("03","Deterministic candidates","Six carried candidate mechanisms received dynamic execution evidence during Phase 6; this does not imply six validated vulnerabilities."),
("04","Pinned Ethereum fork","Phase 7 exercised staking, harvest, withdrawal, conversion and reward behavior on a pinned Ethereum fork, including sdCRV, sdFXN and sdYB paths."),
("05","Independent remediation verification","Phase 9 recorded four independently verified remediations, including executable converter routes, stale rescue timer, sdYB classification and tolerance bounds.")
]:
    rect(35,top-95,525,84,PANEL,stroke=BORDER,radius=7)
    rect(48,top-66,42,42,TEAL,radius=5)
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",13);c.drawCentredString(69,top-49,n)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",11);c.drawString(106,top-36,title)
    para(desc,106,top-54,438,8.9,MUTED,12,3)
    link_area(35,top-95,525,84,("Medusa_Fuzz_Results.json" if n=="01" else "Native_Fuzz_Results.json" if n=="02" else "Execution_Results.json" if n=="03" else "Methodology_and_Analysis.json" if n=="04" else "Findings_and_Remediation.json"))
    top-=108
end()

# 08-09 SEVERITY PAGES — four fixed slots per page, never mixed.
impacts={
"BH-V2-LOW-001":"Marginal share-issuance advantage from temporary reward valuation distortion.",
"BH-V2-LOW-002":"Conversion protection could cause harvest-liveness failure during price divergence.",
"BH-V2-LOW-003":"Privileged owner may rescue disabled-route reward-token balances after delay.",
"BH-V2-LOW-004":"Disabled reward route may prevent later distribution of residual carry.",
"BH-V2-LOW-005":"Pre-aged rescue timer could bypass a fresh warning interval.",
"BH-V2-LOW-006":"Incorrect WANT classification could block sdYB staking construction.",
"BH-V2-RR2-LOW-001":"Exact oracle preview as minOut could revert otherwise normal fee conversions."
}
def finding_page(batch,number,total):
    severity = str(batch[0]["severity"]).lower()
    assert all(str(f["severity"]).lower() == severity for f in batch), "Mixed severity on one page"
    sev_color = SEVERITY_COLORS[severity]
    sev_tint = SEVERITY_TINTS[severity]
    top=start(f"{severity.upper()}-SEVERITY SECURITY FINDINGS",f"Findings {number} of {total}")
    c.setFillColor(sev_color)
    c.setFont("Helvetica-Bold",9.0)
    c.drawString(36,top-4,f"{severity.upper()}  /  {len(batch)} FINDINGS ON THIS PAGE")
    high=top-24;h=150;gap=12
    for i,f in enumerate(batch):
        y=high-(i+1)*h-i*gap
        rect(35,y,525,h,WHITE,stroke=BORDER,radius=7)
        # Severity stripe and pale tint are semantic; status is independent.
        rect(35,y,5,h,sev_color)
        rect(43,y+h-32,387,25,sev_tint,radius=4)
        c.setFillColor(sev_color);c.setFont("Helvetica-Bold",9.4)
        c.drawString(49,y+h-20,f["id"])
        isfixed=f["status"]=="REMEDIATED_VERIFIED"
        status="FIXED / VERIFIED" if isfixed else "ACCEPTED RESIDUAL"
        rect(438,y+h-28,110,18,FIXED_TINT if isfixed else ACCEPTED_TINT,radius=5)
        c.setFillColor(FIXED_COLOR if isfixed else ACCEPTED_COLOR)
        c.setFont("Helvetica-Bold",7.3)
        c.drawCentredString(493,y+h-22,status)
        para(f["title"],49,y+h-38,484,9.1,NAVY,11,2,True)
        c.setFillColor(sev_color);c.setFont("Helvetica-Bold",7.4)
        c.drawString(49,y+75,"DESCRIPTION")
        para(f["description"],49,y+62,486,8.0,INK,10,3)
        c.setFillColor(sev_color);c.setFont("Helvetica-Bold",7.4)
        c.drawString(49,y+28,"SECURITY IMPACT")
        para(impacts[f["id"]],126,y+28,414,7.9,MUTED,10,2)
        c.setFillColor(MUTED);c.setFont("Helvetica",7.1)
        c.drawString(49,y+10,"Finding details, impact and disposition verified in the public findings record")
        link_area(35,y,525,h,"Findings_and_Remediation.json")
    end()

# Keep the four-identical-box rule; never mix severities on a page.
ordered = ["critical", "high", "medium", "low", "informational"]
finding_batches = []
for severity in ordered:
    group = [f for f in findings if str(f["severity"]).lower() == severity]
    for i in range(0,len(group),4):
        finding_batches.append(group[i:i+4])
for i,batch in enumerate(finding_batches,1):
    finding_page(batch,i,len(finding_batches))

# 10 REMEDIATION & RESIDUAL LOW RISK
top=start("Remediation and residual risk","Outcomes")
c.setFillColor(FIXED_COLOR);c.setFont("Helvetica-Bold",11);c.drawString(35,top,"FOUR INDEPENDENTLY VERIFIED FIXES")
top-=24
for f in [x for x in findings if x["status"]=="REMEDIATED_VERIFIED"]:
    rect(35,top-55,525,50,FIXED_TINT,radius=6)
    rect(35,top-55,4,50,FIXED_COLOR)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",8.4);c.drawString(47,top-22,f["id"])
    para(f["title"],200,top-22,344,8.8,INK,12,2)
    link_area(35,top-55,525,50,"Findings_and_Remediation.json")
    top-=65
top-=17
c.setFillColor(ACCEPTED_COLOR);c.setFont("Helvetica-Bold",11)
c.drawString(35,top,"THREE EXPRESSLY ACCEPTED LOW FINDINGS")
top-=25
for f in [x for x in findings if x["status"]=="ACCEPTED"]:
    rect(35,top-50,525,45,ACCEPTED_TINT,radius=6)
    rect(35,top-50,4,45,ACCEPTED_COLOR)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",8.4);c.drawString(47,top-20,f["id"])
    para(f["title"],200,top-20,344,8.5,INK,11,2)
    link_area(35,top-50,525,45,"Findings_and_Remediation.json")
    top-=58
top-=14
para("These accepted issues remain unfixed. They are documented as marginal, bounded economic impact, not as eliminated risk. Further code or configuration changes require their own source-bound review before any equivalence to this audit may be claimed.",35,top,521,9.0,MUTED,13,5)
end()



c.setTitle("CurveYield Boosthub Staking v2 — Security Audit and Public Evidence")
c.setAuthor("CurveYield Security")
c.save()

# Enforce the exact publication policy on the generated PDF before committing.
import fitz
assert OUT.exists() and OUT.stat().st_size > 20000
with fitz.open(OUT) as rendered:
    assert len(rendered) == page_no == 10, f"Unexpected page count: {len(rendered)}"
    uris = [link["uri"] for pg in rendered for link in pg.get_links() if link.get("kind") == fitz.LINK_URI]
    intended = [URL + row[2] for row in links]
    assert len(uris) >= 55, f"Expected context links throughout report, got {len(uris)}"
    # A severity is never defined by its disposition, and every severity color is unique.
    assert len({str(SEVERITY_COLORS[k]) for k in SEVERITY_COLORS}) == len(SEVERITY_COLORS)
    assert all(str(f["severity"]).lower() in SEVERITY_COLORS for f in findings)
    assert set(uris) == set(intended), (set(uris), set(intended))
    assert len(rendered[1].get_links()) >= 9, "Executive content lacks contextual links"
    assert len(rendered[2].get_links()) >= 16 and len(rendered[3].get_links()) >= 16, "Statistic boxes lack evidence links"
    assert len(rendered[-1].get_links()) >= 7, "Finding-resolution descriptions lack links"
    assert not any("curveyield3/Audit-Controller" in uri or "CurveYield2/Audits" in uri for uri in uris)
print(f"Generated {OUT} ({OUT.stat().st_size} bytes); {page_no} pages; {len(uris)} in-context hyperlinks to seven distinct release-local documents; no source ZIP or reference page.")
