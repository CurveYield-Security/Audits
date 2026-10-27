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

NAVY=HexColor("#071D35")
DEEP=HexColor("#102A46")
INK=HexColor("#172E49")
MUTED=HexColor("#5F7486")
TEAL=HexColor("#0D948D")
PALE=HexColor("#EAF7F5")
BLUE=HexColor("#0B7596")
GOLD=HexColor("#E5AB41")
BORDER=HexColor("#D7E3EA")
PANEL=HexColor("#F2F7FA")
WHITE=HexColor("#FFFFFF")
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

# 01 COVER — editorial hero, no duplicated process housekeeping.
page_no+=1
rect(0,0,W,H,NAVY)
rect(0,H-21,W,21,TEAL)
rect(39,515,5,153,TEAL)
c.setFillColor(WHITE);c.setFont("Helvetica-Bold",11)
c.drawString(56,727,"CURVEYIELD  /  SMART-CONTRACT SECURITY")
c.setFont("Helvetica-Bold",32)
c.drawString(56,633,"BOOSTHUB")
c.drawString(56,593,"STAKING V2")
c.setFillColor(HexColor("#B7D5E1"));c.setFont("Helvetica",13)
c.drawString(56,548,"Independent-review process  /  Sealed August 23, 2026")
rect(54,368,487,125,DEEP,radius=10)
c.setFillColor(HexColor("#A3DBD4"));c.setFont("Helvetica-Bold",10)
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
    c.setFillColor(HexColor("#A9C5D4"));c.setFont("Helvetica",7.5);c.drawString(x,210,label)
c.setFillColor(HexColor("#B7D0DB"));c.setFont("Helvetica",8)
c.drawString(56,110,"Scope: audited smart contracts only. No production deployment attestation is claimed.")
c.drawString(56,91,"This release links seven selected public evidence files; the source ZIP is not published.")
c.setFont("Helvetica",7.5);c.drawRightString(541,48,"01")
end()

# 02 EXECUTIVE ASSESSMENT
top=start("Executive security assessment","Executive")
rect(35,top-94,525,91,PALE,radius=9)
c.setFillColor(TEAL);c.setFont("Helvetica-Bold",10)
c.drawString(51,top-27,"COMPLETED REVIEW  •  SECURITY VERDICT: PASS")
para("The completed V7 audit validated seven Low-severity findings. Four were remediated and independently verified. The remaining three are expressly accepted as marginal, bounded economic impact; they are not fixed.",51,top-48,490,9.6,INK,14,3)
top-=125
for head,body in [
("What was examined","Vault and staking-contract principal flows, reward accounting, share issuance, conversion routes, governance privileges, token interfaces and external dependency behavior."),
("What the verdict means","No unresolved unaccepted security findings remain within the admitted smart-contract scope. The three accepted Low findings remain present and are identified by finding ID."),
("Security assurance boundaries","The review assessed source-bound contract behavior and recorded test evidence. It does not certify deployment scripts, release tooling, operator workflow, future market conditions or production configuration."),
("Assurance independence","The recorded reviewer model is procedural independence only. This report does not claim a blind external third-party audit.")
]:
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",12);c.drawString(36,top,head)
    top=para(body,36,top-19,516,9.5,MUTED,14)-26
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
        top-=math.ceil(len(entries)/cols)*(ch+8)+27
    end()

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
c.setFillColor(WHITE);c.setFont("Helvetica-Bold",28);c.drawString(51,top-55,"7 LOW")
c.setFont("Helvetica",11);c.setFillColor(HexColor("#BDD1DE"))
c.drawString(51,top-85,"No validated Critical, High or Medium findings")
rect(292,top-101,116,67,HexColor("#173E51"),radius=6)
rect(422,top-101,116,67,HexColor("#173E51"),radius=6)
for x,num,lbl in [(306,"4","FIXED / VERIFIED"),(435,"3","ACCEPTED LOW")]:
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",22);c.drawString(x,top-72,num)
    c.setFont("Helvetica",7);c.drawString(x,top-89,lbl)
top-=157
c.setFillColor(NAVY);c.setFont("Helvetica-Bold",11);c.drawString(35,top,"VALIDATED FINDING SEVERITY")
top-=27
for label,val,color in [("Critical",0,HexColor("#A92E3B")),("High",0,HexColor("#E16F40")),("Medium",0,GOLD),("Low",7,BLUE)]:
    c.setFont("Helvetica-Bold",9);c.setFillColor(INK);c.drawString(37,top,label)
    rect(111,top-2,405,11,PANEL,radius=4)
    if val: rect(111,top-2,405*val/7,11,color,radius=4)
    c.drawRightString(550,top,str(val));top-=39
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
    top=para(desc,35,top-18,522,9.2,MUTED,13,3)-31
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
    top=start("LOW-SEVERITY SECURITY FINDINGS",f"Findings {number} of {total}")
    c.setFillColor(MUTED);c.setFont("Helvetica",8)
    c.drawString(36,top-4,"Four fixed-size boxes per severity page. Open slots remain blank.")
    high=top-24;h=150;gap=12
    for i,f in enumerate(batch):
        y=high-(i+1)*h-i*gap
        rect(35,y,525,h,WHITE,stroke=BORDER,radius=7)
        rect(35,y,5,h,BLUE)
        c.setFillColor(NAVY);c.setFont("Helvetica-Bold",9.4)
        c.drawString(49,y+h-20,f["id"])
        isfixed=f["status"]=="REMEDIATED_VERIFIED"
        status="FIXED / VERIFIED" if isfixed else "ACCEPTED RESIDUAL"
        rect(438,y+h-28,110,18,PALE if isfixed else HexColor("#FFF3DC"),radius=5)
        c.setFillColor(TEAL if isfixed else HexColor("#A86915"));c.setFont("Helvetica-Bold",7.3)
        c.drawCentredString(493,y+h-22,status)
        para(f["title"],49,y+h-38,484,9.1,NAVY,11,2,True)
        c.setFillColor(TEAL);c.setFont("Helvetica-Bold",7.4);c.drawString(49,y+75,"DESCRIPTION")
        para(f["description"],49,y+62,486,8.0,INK,10,3)
        c.setFillColor(TEAL);c.setFont("Helvetica-Bold",7.4);c.drawString(49,y+28,"SECURITY IMPACT")
        para(impacts[f["id"]],126,y+28,414,7.9,MUTED,10,2)
        c.setFillColor(MUTED);c.setFont("Helvetica",7.1);c.drawString(49,y+10,"Complete evidence and disposition: Findings_and_Remediation.json")
    end()
finding_page(findings[:4],1,2)
finding_page(findings[4:],2,2)

# 10 REMEDIATION & RESIDUAL LOW RISK
top=start("Remediation and residual risk","Outcomes")
c.setFillColor(TEAL);c.setFont("Helvetica-Bold",11);c.drawString(35,top,"FOUR INDEPENDENTLY VERIFIED FIXES")
top-=24
for f in [x for x in findings if x["status"]=="REMEDIATED_VERIFIED"]:
    rect(35,top-55,525,50,PANEL,radius=6)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",8.4);c.drawString(47,top-22,f["id"])
    para(f["title"],200,top-22,344,8.8,INK,12,2)
    top-=65
top-=17
c.setFillColor(HexColor("#A46816"));c.setFont("Helvetica-Bold",11)
c.drawString(35,top,"THREE EXPRESSLY ACCEPTED LOW FINDINGS")
top-=25
for f in [x for x in findings if x["status"]=="ACCEPTED"]:
    rect(35,top-50,525,45,HexColor("#FFF8EA"),radius=6)
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",8.4);c.drawString(47,top-20,f["id"])
    para(f["title"],200,top-20,344,8.5,INK,11,2)
    top-=58
top-=14
para("These accepted issues remain unfixed. They are documented as marginal, bounded economic impact, not as eliminated risk. Further code or configuration changes require their own source-bound review before any equivalence to this audit may be claimed.",35,top,521,9.0,MUTED,13,5)
end()

# 11 CURATED PUBLIC REFERENCES
top=start("Explore the audit evidence","Public files")
rect(35,top-54,525,45,PALE,radius=6)
c.setFillColor(TEAL);c.setFont("Helvetica-Bold",9.3)
c.drawString(47,top-32,"SEVEN SELECTED PUBLIC FILES   /   SOURCE ZIP NOT PUBLISHED")
top-=75
for i,(title,description,filename) in enumerate(links,1):
    y=top-64
    rect(35,y,525,58,PANEL if i%2 else WHITE,stroke=BORDER,radius=6)
    rect(46,y+16,32,31,TEAL,radius=5)
    c.setFillColor(WHITE);c.setFont("Helvetica-Bold",10)
    c.drawCentredString(62,y+26,f"{i:02}")
    c.setFillColor(NAVY);c.setFont("Helvetica-Bold",10.5)
    c.drawString(91,y+39,title)
    c.setFillColor(MUTED);c.setFont("Helvetica",8)
    c.drawString(91,y+23,description)
    c.setFillColor(TEAL);c.setFont("Helvetica-Bold",7.7)
    c.drawString(91,y+10,"OPEN PUBLIC RECORD")
    c.linkURL(URL+filename,(35,y,560,y+58),relative=0,thickness=0)
    top-=73
para("These files were already publicly released as sanitized audit evidence. No source ZIP has been reconstructed or published. This report creates no links into private audit infrastructure.",35,top-12,520,8.3,MUTED,12,3)
end()

c.setTitle("CurveYield Boosthub Staking v2 — Security Audit and Public Evidence")
c.setAuthor("CurveYield Security")
c.save()

# Lightweight structural verification: pdfinfo via PyMuPDF is not required.
from pathlib import Path
assert OUT.exists() and OUT.stat().st_size > 20000
print(f"Generated {OUT} ({OUT.stat().st_size} bytes); {page_no} pages; seven release-local evidence URLs.")
