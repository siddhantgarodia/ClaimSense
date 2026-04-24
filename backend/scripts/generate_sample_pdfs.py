"""
Generates realistic sample policy and claim PDFs for testing ClaimSense.
Run once before starting the server: python scripts/generate_sample_pdfs.py
"""
from pathlib import Path
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

BASE_DIR = Path(__file__).parent.parent
POLICIES_DIR = BASE_DIR / "data" / "sample_policies"
CLAIMS_DIR = BASE_DIR / "data" / "sample_claims"


def _make_doc(path: Path, title: str):
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("Heading1Custom", parent=styles["Heading1"], fontSize=16, spaceAfter=12, alignment=TA_CENTER)
    subheading = ParagraphStyle("Heading2Custom", parent=styles["Heading2"], fontSize=12, spaceAfter=8)
    body = ParagraphStyle("BodyCustom", parent=styles["Normal"], fontSize=10, spaceAfter=6, leading=14)
    bold = ParagraphStyle("BoldCustom", parent=styles["Normal"], fontSize=10, spaceAfter=4, fontName="Helvetica-Bold")
    return doc, heading, subheading, body, bold


def generate_motor_policy():
    path = POLICIES_DIR / "motor_policy.pdf"
    doc, heading, subheading, body, bold = _make_doc(path, "Motor Insurance Policy")
    story = [
        Paragraph("SECURE INDIA GENERAL INSURANCE", heading),
        Paragraph("Motor Vehicle Insurance Policy", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("POLICY TYPE: Comprehensive Motor Vehicle Insurance", bold),
        Paragraph("Policy Series: POL-MOT-XXXXX", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("1. COVERAGE SUMMARY", subheading),
        Paragraph(
            "This policy provides comprehensive coverage for private motor vehicles registered in India. "
            "Coverage includes accidental damage, theft, third-party liability, and natural calamity damage. "
            "The maximum coverage limit under this policy is INR 500,000 (Five Lakh Rupees) per claim event.",
            body,
        ),
        Paragraph("Maximum Coverage Amount: INR 500,000", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("2. COVERED EVENTS", subheading),
        Paragraph(
            "The following events are covered under this policy:\n"
            "- Accidental collision damage to the insured vehicle\n"
            "- Theft or attempted theft of the insured vehicle\n"
            "- Third-party bodily injury and property damage liability\n"
            "- Fire and explosion damage\n"
            "- Natural calamities: flood, earthquake, cyclone, hailstorm\n"
            "- Malicious damage by third parties\n"
            "- Damage during transit by road, rail, inland waterway, lift or elevator",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("3. EXCLUSIONS", subheading),
        Paragraph(
            "Claims will NOT be payable under any of the following circumstances:\n"
            "- Vehicle driven under the influence of alcohol or drugs\n"
            "- Vehicle used for racing, speed testing, or reliability trials\n"
            "- Vehicle driven by an unlicensed driver or a driver whose license has expired\n"
            "- Damage caused by wear and tear, mechanical or electrical breakdown\n"
            "- Consequential loss, depreciation, or loss of use\n"
            "- Damage outside geographical limits of India\n"
            "- Claims reported more than 90 days after the date of incident without valid reason",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("4. CLAIM PROCEDURE", subheading),
        Paragraph(
            "To file a claim, the policyholder must: (1) Notify the insurer within 48 hours of the incident. "
            "(2) Submit a completed claim form with supporting documents including FIR (if applicable), "
            "repair estimate, photographs of damage, and original policy documents. "
            "(3) Cooperate with the surveyor appointed by the insurer. "
            "Claims must be filed within 90 days of the incident date. Late claims may be rejected.",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("5. POLICY PERIOD AND RENEWAL", subheading),
        Paragraph(
            "This policy is valid for a period of one year from the date of issuance. "
            "Renewal must be completed before the expiry date to maintain continuous coverage. "
            "A grace period of 30 days is allowed for renewal; however, claims during the grace period "
            "are not payable unless the renewal premium has been received.",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("6. DEDUCTIBLES", subheading),
        Paragraph(
            "A compulsory deductible of INR 1,000 applies to all own-damage claims. "
            "A voluntary deductible of up to INR 15,000 may be opted for a premium discount. "
            "The deductible amount is subtracted from the total approved claim amount before payment.",
            body,
        ),
    ]
    doc.build(story)
    print(f"  Created: {path}")


def generate_health_policy():
    path = POLICIES_DIR / "health_policy.pdf"
    doc, heading, subheading, body, bold = _make_doc(path, "Health Insurance Policy")
    story = [
        Paragraph("SECURE INDIA GENERAL INSURANCE", heading),
        Paragraph("Individual Health Insurance Policy", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("POLICY TYPE: Individual Health & Hospitalization Insurance", bold),
        Paragraph("Policy Series: POL-HLT-XXXXX", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("1. COVERAGE SUMMARY", subheading),
        Paragraph(
            "This policy provides comprehensive health insurance coverage for the insured individual. "
            "It covers hospitalization expenses, surgical procedures, diagnostic tests, and post-hospitalization care. "
            "The maximum sum insured under this policy is INR 300,000 (Three Lakh Rupees) per policy year.",
            body,
        ),
        Paragraph("Maximum Coverage Amount: INR 300,000 per policy year", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("2. COVERED BENEFITS", subheading),
        Paragraph(
            "The following benefits are covered:\n"
            "- In-patient hospitalization for illness or injury requiring admission for at least 24 hours\n"
            "- Day-care procedures that require less than 24-hour hospitalization\n"
            "- Pre-hospitalization expenses up to 30 days before admission\n"
            "- Post-hospitalization expenses up to 60 days after discharge\n"
            "- Emergency ambulance charges up to INR 2,000 per hospitalization\n"
            "- Surgical procedures including anaesthesia and operation theatre charges\n"
            "- ICU charges, nursing charges, and doctor consultation fees during hospitalization",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("3. EXCLUSIONS", subheading),
        Paragraph(
            "The following conditions are NOT covered under this policy:\n"
            "- Pre-existing diseases and conditions for the first 24 months of the policy\n"
            "- Cosmetic surgery, plastic surgery, or aesthetic treatments unless medically necessary\n"
            "- Treatment for self-inflicted injuries or attempted suicide\n"
            "- Experimental treatments or unproven medical procedures\n"
            "- Dental treatment other than accidental injury to natural teeth\n"
            "- Congenital anomalies and genetic disorders\n"
            "- Treatment outside India\n"
            "- Claims arising from war, terrorism, or nuclear hazards",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("4. WAITING PERIODS", subheading),
        Paragraph(
            "Initial waiting period: 30 days from policy commencement for all illnesses (accidents excluded). "
            "Pre-existing disease waiting period: 24 months of continuous coverage. "
            "Specific disease waiting period: 12 months for listed conditions including hernia, cataract, "
            "kidney stones, joint replacement, and varicose veins.",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("5. CLAIM PROCESS", subheading),
        Paragraph(
            "For cashless claims: Contact the insurer's 24-hour helpline before or within 24 hours of admission. "
            "Submit the pre-authorization form at the hospital insurance desk. "
            "For reimbursement claims: Submit original bills, discharge summary, and medical reports "
            "within 30 days of discharge. Claims must be intimated within 24 hours of hospitalization.",
            body,
        ),
    ]
    doc.build(story)
    print(f"  Created: {path}")


def generate_home_policy():
    path = POLICIES_DIR / "home_policy.pdf"
    doc, heading, subheading, body, bold = _make_doc(path, "Home Insurance Policy")
    story = [
        Paragraph("SECURE INDIA GENERAL INSURANCE", heading),
        Paragraph("Comprehensive Home Insurance Policy", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("POLICY TYPE: Home Structure and Contents Insurance", bold),
        Paragraph("Policy Series: POL-HOM-XXXXX", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("1. COVERAGE SUMMARY", subheading),
        Paragraph(
            "This policy provides comprehensive protection for your home structure and household contents. "
            "Coverage extends to the building structure, permanent fixtures, and personal belongings. "
            "The maximum coverage limit is INR 800,000 (Eight Lakh Rupees) for structure and INR 200,000 for contents.",
            body,
        ),
        Paragraph("Maximum Coverage Amount: INR 800,000 (structure) + INR 200,000 (contents)", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("2. COVERED PERILS", subheading),
        Paragraph(
            "The following perils are covered:\n"
            "- Fire and explosion\n"
            "- Lightning strike\n"
            "- Theft and burglary (with evidence of forcible entry)\n"
            "- Natural disasters: earthquake, flood, cyclone, storm, hailstorm, landslide\n"
            "- Aircraft damage\n"
            "- Riot, strike, and malicious damage\n"
            "- Burst or overflowing of water tanks, pipes, or apparatus\n"
            "- Impact damage from vehicles or falling trees",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("3. EXCLUSIONS", subheading),
        Paragraph(
            "The following are NOT covered:\n"
            "- Gradual deterioration, wear and tear, or lack of maintenance\n"
            "- War, invasion, civil war, or nuclear hazard\n"
            "- Wilful destruction or negligence by the insured\n"
            "- Loss of data stored on computers or electronic devices\n"
            "- Land subsidence (unless caused by earthquake)\n"
            "- Loss of cash, securities, or documents\n"
            "- Property under construction\n"
            "- Consequential losses or loss of rental income",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("4. SUM INSURED BASIS", subheading),
        Paragraph(
            "The building structure is insured on reinstatement value basis — the cost to rebuild the structure "
            "to the same specification using current material and labour costs. "
            "Contents are insured on market value basis after deducting depreciation based on age and condition.",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("5. CLAIM REQUIREMENTS", subheading),
        Paragraph(
            "To file a home insurance claim: (1) Report the incident to local authorities (police/fire brigade) "
            "and obtain a copy of the report. (2) Notify the insurer within 48 hours. "
            "(3) Preserve all damaged items for surveyor inspection — do not dispose of them without insurer approval. "
            "(4) Submit claim form with photos, repair estimates, and authority report within 15 days.",
            body,
        ),
    ]
    doc.build(story)
    print(f"  Created: {path}")


def generate_motor_valid_claim():
    path = CLAIMS_DIR / "claim_motor_valid.pdf"
    doc, heading, subheading, body, bold = _make_doc(path, "Motor Claim Form")
    story = [
        Paragraph("INSURANCE CLAIM FORM", heading),
        Paragraph("Motor Vehicle Claim", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("Claimant Name: Rajesh Kumar", bold),
        Paragraph("Policy Number: POL-MOT-12345", bold),
        Paragraph("Claim Type: Motor", bold),
        Paragraph("Incident Date: 2026-03-15", bold),
        Paragraph("Amount Claimed: INR 45,000", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("Incident Description:", subheading),
        Paragraph(
            "On the morning of March 15, 2026, I was driving my vehicle (Honda City, MH-12-AB-1234) "
            "along the Pune-Mumbai Expressway near Khopoli. A truck ahead of me braked suddenly due to road "
            "construction, and despite applying brakes immediately, my vehicle sustained a rear-end collision. "
            "The impact caused significant damage to the front bumper, hood, and headlight assembly. "
            "I was driving at approximately 80 km/h within the speed limit. No third-party injuries occurred. "
            "A police report was filed at Khopoli Police Station on the same day (FIR No. KHP/2026/0315/042).",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Damage Items:", subheading),
        Paragraph("- Front bumper replacement: INR 12,000", body),
        Paragraph("- Hood panel repair and repainting: INR 18,000", body),
        Paragraph("- Headlight assembly (left): INR 8,500", body),
        Paragraph("- Radiator grill replacement: INR 3,500", body),
        Paragraph("- Labour and miscellaneous charges: INR 3,000", body),
        Spacer(1, 0.3 * cm),
        Paragraph("Supporting Documents:", subheading),
        Paragraph("- Copy of driving licence (valid until 2028-06-30)", body),
        Paragraph("- Vehicle registration certificate", body),
        Paragraph("- FIR copy from Khopoli Police Station", body),
        Paragraph("- Repair estimate from authorised Honda service centre", body),
        Paragraph("- Photographs of damage (12 photos attached)", body),
        Spacer(1, 0.3 * cm),
        Paragraph(
            "I hereby declare that the information provided above is true and correct to the best of my knowledge. "
            "I have not made any previous claim for this incident.",
            body,
        ),
        Spacer(1, 0.2 * cm),
        Paragraph("Signature: Rajesh Kumar", bold),
        Paragraph("Date: 2026-03-22", bold),
    ]
    doc.build(story)
    print(f"  Created: {path}")


def generate_health_valid_claim():
    path = CLAIMS_DIR / "claim_health_valid.pdf"
    doc, heading, subheading, body, bold = _make_doc(path, "Health Claim Form")
    story = [
        Paragraph("INSURANCE CLAIM FORM", heading),
        Paragraph("Health and Hospitalization Claim", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("Claimant Name: Priya Sharma", bold),
        Paragraph("Policy Number: POL-HLT-67890", bold),
        Paragraph("Claim Type: Health", bold),
        Paragraph("Incident Date: 2026-02-10", bold),
        Paragraph("Amount Claimed: INR 80,000", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("Incident Description:", subheading),
        Paragraph(
            "I was admitted to Fortis Hospital, Bangalore on February 10, 2026 for an emergency appendectomy. "
            "I had been experiencing severe abdominal pain for two days prior to admission. "
            "Upon examination, the doctor diagnosed acute appendicitis requiring immediate surgical intervention. "
            "The laparoscopic appendectomy was performed successfully on February 10, 2026. "
            "I was discharged on February 13, 2026 after three days of post-operative care in the hospital. "
            "This is not a pre-existing condition; I have never had appendicitis before. "
            "The surgery was medically necessary and performed by Dr. Anand Krishnamurthy, MS (Surgery).",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Damage Items:", subheading),
        Paragraph("- Hospital room charges (3 nights): INR 18,000", body),
        Paragraph("- Surgical procedure and operation theatre charges: INR 35,000", body),
        Paragraph("- Anaesthesia charges: INR 8,000", body),
        Paragraph("- ICU charges (1 night post-surgery): INR 12,000", body),
        Paragraph("- Medicines and consumables: INR 4,500", body),
        Paragraph("- Diagnostic tests (blood work, ultrasound, CT scan): INR 2,500", body),
        Spacer(1, 0.3 * cm),
        Paragraph("Supporting Documents:", subheading),
        Paragraph("- Hospital discharge summary", body),
        Paragraph("- Original bills and receipts from Fortis Hospital", body),
        Paragraph("- Surgeon's certificate and operative notes", body),
        Paragraph("- All diagnostic test reports", body),
        Paragraph("- Prescription and pharmacy receipts", body),
        Spacer(1, 0.3 * cm),
        Paragraph(
            "I confirm that this hospitalization was not for a pre-existing condition. "
            "I have not received any other insurance claims for this hospitalization.",
            body,
        ),
        Spacer(1, 0.2 * cm),
        Paragraph("Signature: Priya Sharma", bold),
        Paragraph("Date: 2026-02-20", bold),
    ]
    doc.build(story)
    print(f"  Created: {path}")


def generate_suspicious_claim():
    path = CLAIMS_DIR / "claim_suspicious.pdf"
    # Incident 120 days ago from today
    incident_date = (date.today() - timedelta(days=120)).isoformat()
    doc, heading, subheading, body, bold = _make_doc(path, "Motor Claim Form")
    story = [
        Paragraph("INSURANCE CLAIM FORM", heading),
        Paragraph("Motor Vehicle Claim", subheading),
        HRFlowable(width="100%", thickness=1, spaceAfter=12),
        Paragraph("Claimant Name: Vikram Malhotra", bold),
        Paragraph("Policy Number: POL-MOT-99999", bold),
        Paragraph("Claim Type: Motor", bold),
        Paragraph(f"Incident Date: {incident_date}", bold),
        Paragraph("Amount Claimed: INR 500,000", bold),
        Spacer(1, 0.3 * cm),
        Paragraph("Incident Description:", subheading),
        Paragraph(
            "The vehicle was damaged due to an accident. Various parts of the vehicle were badly damaged "
            "and need to be replaced. The vehicle is currently not in working condition. "
            "The incident happened on the road. All damage occurred during the incident.",
            body,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Damage Items:", subheading),
        Paragraph("- Complete vehicle damage: INR 200,000", body),
        Paragraph("- Engine replacement: INR 150,000", body),
        Paragraph("- Transmission and gearbox: INR 100,000", body),
        Paragraph("- All body panels: INR 50,000", body),
        Spacer(1, 0.3 * cm),
        Paragraph("Supporting Documents:", subheading),
        Paragraph("- Documents will be submitted later", body),
        Spacer(1, 0.3 * cm),
        Paragraph(
            "I declare that the above information is correct.",
            body,
        ),
        Spacer(1, 0.2 * cm),
        Paragraph("Signature: Vikram Malhotra", bold),
        Paragraph(f"Date: {date.today().isoformat()}", bold),
    ]
    doc.build(story)
    print(f"  Created: {path}")


if __name__ == "__main__":
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating policy PDFs...")
    generate_motor_policy()
    generate_health_policy()
    generate_home_policy()

    print("\nGenerating claim PDFs...")
    generate_motor_valid_claim()
    generate_health_valid_claim()
    generate_suspicious_claim()

    print("\nAll sample PDFs generated successfully.")
