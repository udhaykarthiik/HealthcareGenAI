"""
Generate sample medical documents for testing the Healthcare AI Assistant
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime

def create_discharge_summary():
    """Create a sample discharge summary PDF"""
    filename = "sample_documents/discharge_summary.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
    story.append(Paragraph("HOSPITAL DISCHARGE SUMMARY", title_style))
    story.append(Spacer(1, 12))
    
    # Patient Information
    story.append(Paragraph("<b>PATIENT INFORMATION</b>", styles['Heading2']))
    story.append(Paragraph("Name: Sarah Johnson", styles['Normal']))
    story.append(Paragraph("Age: 58 years", styles['Normal']))
    story.append(Paragraph("Gender: Female", styles['Normal']))
    story.append(Paragraph("MRN: 12345678", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Admission Details
    story.append(Paragraph("<b>ADMISSION DETAILS</b>", styles['Heading2']))
    story.append(Paragraph("Admission Date: March 10, 2026", styles['Normal']))
    story.append(Paragraph("Discharge Date: March 18, 2026", styles['Normal']))
    story.append(Paragraph("Admitting Physician: Dr. James Wilson, Cardiology", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Principal Diagnosis
    story.append(Paragraph("<b>PRINCIPAL DIAGNOSIS</b>", styles['Heading2']))
    story.append(Paragraph("Acute Myocardial Infarction (STEMI) - Anterolateral wall", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Secondary Diagnoses
    story.append(Paragraph("<b>SECONDARY DIAGNOSES</b>", styles['Heading2']))
    story.append(Paragraph("- Hypertension (Essential)", styles['Normal']))
    story.append(Paragraph("- Type 2 Diabetes Mellitus", styles['Normal']))
    story.append(Paragraph("- Hyperlipidemia", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Hospital Course
    story.append(Paragraph("<b>HOSPITAL COURSE</b>", styles['Heading2']))
    course_text = """Patient presented to ED with crushing chest pain radiating to left arm, diaphoresis, and shortness of breath. ECG showed ST elevation in leads V1-V4. Emergent cardiac catheterization revealed 95% stenosis in LAD. Successful drug-eluting stent placement. Post-procedure course uncomplicated. Patient remained hemodynamically stable. Cardiology consulted for optimal medical management. Patient received education on cardiac rehabilitation, medication adherence, and lifestyle modifications. No complications noted during hospitalization."""
    story.append(Paragraph(course_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Medications at Discharge
    story.append(Paragraph("<b>MEDICATIONS AT DISCHARGE</b>", styles['Heading2']))
    meds = [
        ["Aspirin", "81mg", "Once daily", "PO"],
        ["Clopidogrel", "75mg", "Once daily", "PO"],
        ["Atorvastatin", "80mg", "Once daily at bedtime", "PO"],
        ["Metoprolol", "50mg", "Twice daily", "PO"],
        ["Lisinopril", "10mg", "Once daily", "PO"]
    ]
    med_table = Table([["Medication", "Dosage", "Frequency", "Route"]] + meds, colWidths=[150, 80, 100, 60])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(med_table)
    story.append(Spacer(1, 12))
    
    # Discharge Instructions
    story.append(Paragraph("<b>DISCHARGE INSTRUCTIONS</b>", styles['Heading2']))
    instructions = """
    - Follow up with cardiology in 7 days
    - Cardiac rehabilitation program recommended - call to schedule
    - Low sodium, low fat diet
    - No strenuous activity for 2 weeks
    - Monitor for chest pain, shortness of breath, or dizziness
    - Take all medications as prescribed
    - Bring medication list to all appointments
    """
    story.append(Paragraph(instructions, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Follow-up Plan
    story.append(Paragraph("<b>FOLLOW-UP PLAN</b>", styles['Heading2']))
    story.append(Paragraph("Cardiology: March 25, 2026 with Dr. James Wilson", styles['Normal']))
    story.append(Paragraph("Primary Care: March 28, 2026 with Dr. Emily Chen", styles['Normal']))
    story.append(Paragraph("Lab Work: CBC, CMP, Lipid Panel in 2 weeks", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Signatures
    story.append(Paragraph("Discharging Physician: _________________ Dr. James Wilson", styles['Normal']))
    story.append(Paragraph("Date: March 18, 2026", styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_referral_letter():
    """Create a sample referral letter PDF"""
    filename = "sample_documents/referral_letter.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("MEDICAL REFERRAL LETTER", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>REFERRING PHYSICIAN:</b>", styles['Heading2']))
    story.append(Paragraph("Dr. Michael Thompson, MD", styles['Normal']))
    story.append(Paragraph("Internal Medicine", styles['Normal']))
    story.append(Paragraph("123 Main Street, Suite 100", styles['Normal']))
    story.append(Paragraph("Phone: (555) 123-4567", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>PATIENT INFORMATION:</b>", styles['Heading2']))
    story.append(Paragraph("Name: Robert Williams", styles['Normal']))
    story.append(Paragraph("DOB: 02/15/1965 (Age: 61)", styles['Normal']))
    story.append(Paragraph("MRN: 98765432", styles['Normal']))
    story.append(Paragraph("Insurance: Blue Cross Blue Shield", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>REFERRAL DATE:</b>", styles['Heading2']))
    story.append(Paragraph("March 20, 2026", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>REASON FOR REFERRAL:</b>", styles['Heading2']))
    story.append(Paragraph("Evaluation and management of new-onset seizures", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>RELEVANT MEDICAL HISTORY:</b>", styles['Heading2']))
    history = """Patient has history of hypertension and type 2 diabetes. No prior history of seizures or neurological disorders. 
    Patient was found unconscious at home by family member on March 18, 2026. Witnessed generalized tonic-clonic seizure lasting approximately 2 minutes. 
    Patient was transported to emergency department. CT head showed no acute abnormalities. Labs including electrolytes and glucose were within normal limits. 
    Patient currently on Metformin 1000mg twice daily and Lisinopril 20mg daily."""
    story.append(Paragraph(history, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>CLINICAL FINDINGS:</b>", styles['Heading2']))
    findings = """- Neurological exam: Alert and oriented, no focal deficits
    - Vital signs: BP 138/85, HR 88, Temp 98.6°F
    - ECG: Normal sinus rhythm
    - MRI Brain: Pending
    - EEG: Pending"""
    story.append(Paragraph(findings, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>SPECIALIST REQUESTED:</b>", styles['Heading2']))
    story.append(Paragraph("Neurology - Dr. Sarah Martinez", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>URGENCY LEVEL:</b>", styles['Heading2']))
    story.append(Paragraph("URGENT - Please see within 1 week", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>SPECIFIC QUESTIONS:</b>", styles['Heading2']))
    questions = """1. Etiology of new-onset seizures
    2. Need for anti-epileptic medication
    3. Driving restrictions and recommendations
    4. Further diagnostic testing required"""
    story.append(Paragraph(questions, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_insurance_auth():
    """Create a sample insurance authorization request PDF"""
    filename = "sample_documents/insurance_authorization.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("PRIOR AUTHORIZATION REQUEST", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>PATIENT INFORMATION:</b>", styles['Heading2']))
    story.append(Paragraph("Name: Emily Davis", styles['Normal']))
    story.append(Paragraph("DOB: 08/22/1978 (Age: 47)", styles['Normal']))
    story.append(Paragraph("Insurance ID: BCBS-87654321", styles['Normal']))
    story.append(Paragraph("Group Number: GRP-9876", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>PROVIDER INFORMATION:</b>", styles['Heading2']))
    story.append(Paragraph("Requesting Physician: Dr. Robert Chen, Orthopedic Surgery", styles['Normal']))
    story.append(Paragraph("NPI: 1234567890", styles['Normal']))
    story.append(Paragraph("Practice: Advanced Orthopedics Associates", styles['Normal']))
    story.append(Paragraph("Phone: (555) 987-6543", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>REQUESTED SERVICE/PROCEDURE:</b>", styles['Heading2']))
    story.append(Paragraph("Total Right Knee Arthroplasty (Knee Replacement)", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>DIAGNOSIS CODES (ICD-10):</b>", styles['Heading2']))
    story.append(Paragraph("M17.11 - Unilateral primary osteoarthritis, right knee", styles['Normal']))
    story.append(Paragraph("M25.561 - Pain in right knee", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>PROCEDURE CODES (CPT):</b>", styles['Heading2']))
    story.append(Paragraph("27447 - Arthroplasty, knee, condyle and plateau, medial AND lateral compartments", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>CLINICAL JUSTIFICATION:</b>", styles['Heading2']))
    justification = """Patient presents with severe right knee pain for 3 years. Failed conservative management including:
    - NSAIDs for 6 months
    - Physical therapy for 12 weeks (completed 3 courses)
    - Corticosteroid injections (3 injections, last in January 2026)
    - Viscosupplementation (2 injections)
    
    X-rays show severe joint space narrowing, osteophyte formation, and subchondral sclerosis consistent with end-stage osteoarthritis. Patient reports pain at rest, nighttime pain interfering with sleep, and functional limitations including inability to walk more than 1 block without severe pain. Patient requires surgery to restore function and quality of life."""
    story.append(Paragraph(justification, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>SUPPORTING DOCUMENTATION:</b>", styles['Heading2']))
    story.append(Paragraph("- X-ray images (dated 03/15/2026)", styles['Normal']))
    story.append(Paragraph("- Physical therapy notes (12/2025 - 02/2026)", styles['Normal']))
    story.append(Paragraph("- Office visit notes documenting failed conservative care", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>URGENCY LEVEL:</b>", styles['Heading2']))
    story.append(Paragraph("Standard - Surgery scheduled for April 15, 2026", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>ALTERNATIVE TREATMENTS CONSIDERED:</b>", styles['Heading2']))
    story.append(Paragraph("Arthroscopic debridement (considered but not appropriate for end-stage arthritis), Continued conservative care (failed), Bracing (tried without significant relief)", styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_lab_report():
    """Create a sample lab report PDF"""
    filename = "sample_documents/lab_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("LABORATORY REPORT", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>PATIENT INFORMATION:</b>", styles['Heading2']))
    story.append(Paragraph("Name: David Miller", styles['Normal']))
    story.append(Paragraph("Age: 52 years", styles['Normal']))
    story.append(Paragraph("Gender: Male", styles['Normal']))
    story.append(Paragraph("MRN: 45678912", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>TEST DATE:</b>", styles['Heading2']))
    story.append(Paragraph("March 19, 2026 - 08:45 AM", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>ORDERING PHYSICIAN:</b>", styles['Heading2']))
    story.append(Paragraph("Dr. Lisa Wong, Primary Care", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>LABORATORY RESULTS:</b>", styles['Heading2']))
    
    # Lab results table
    lab_data = [
        ["Test", "Result", "Reference Range", "Flag"],
        ["Hemoglobin", "14.2 g/dL", "13.5-17.5", "Normal"],
        ["WBC Count", "11,500 /µL", "4,500-11,000", "⚠️ High"],
        ["Platelets", "250,000 /µL", "150,000-450,000", "Normal"],
        ["Glucose", "245 mg/dL", "70-100", "⚠️ High"],
        ["HbA1c", "8.5%", "<5.7%", "⚠️ High"],
        ["Cholesterol", "245 mg/dL", "<200", "⚠️ High"],
        ["LDL", "165 mg/dL", "<100", "⚠️ High"],
        ["HDL", "35 mg/dL", ">40", "⚠️ Low"],
        ["Triglycerides", "225 mg/dL", "<150", "⚠️ High"],
        ["Creatinine", "1.1 mg/dL", "0.7-1.3", "Normal"],
        ["ALT", "45 U/L", "10-40", "⚠️ High"],
        ["AST", "42 U/L", "10-40", "⚠️ High"]
    ]
    
    lab_table = Table(lab_data, colWidths=[100, 80, 100, 60])
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (3, 1), (3, 12), colors.yellow)  # Highlight flagged results
    ]))
    story.append(lab_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>CRITICAL/ABNORMAL FINDINGS:</b>", styles['Heading2']))
    abnormal = """⚠️ CRITICAL: Glucose 245 mg/dL (severely elevated)
    ⚠️ HbA1c 8.5% - Poor diabetic control
    ⚠️ Lipid panel abnormal - elevated cholesterol, LDL, triglycerides
    ⚠️ Mild elevation of liver enzymes (ALT, AST)"""
    story.append(Paragraph(abnormal, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>CLINICAL SIGNIFICANCE:</b>", styles['Heading2']))
    significance = """Results indicate poorly controlled type 2 diabetes mellitus and hyperlipidemia. 
    Elevated liver enzymes may be related to fatty liver disease or medication effect. 
    WBC elevation suggests possible underlying infection or inflammation. 
    Immediate intervention needed to address blood glucose and lipid management."""
    story.append(Paragraph(significance, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>RECOMMENDATIONS:</b>", styles['Heading2']))
    recommendations = """1. Start insulin therapy or adjust oral hypoglycemics
    2. Initiate statin therapy for lipid management
    3. Follow-up within 1 week to reassess blood glucose
    4. Evaluate for possible infection
    5. Ultrasound liver to assess for fatty liver disease"""
    story.append(Paragraph(recommendations, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_general_visit():
    """Create a sample general medical visit note PDF"""
    filename = "sample_documents/general_visit.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("OUTPATIENT CLINICAL NOTE", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>PATIENT INFORMATION:</b>", styles['Heading2']))
    story.append(Paragraph("Name: Maria Garcia", styles['Normal']))
    story.append(Paragraph("Age: 34 years", styles['Normal']))
    story.append(Paragraph("Gender: Female", styles['Normal']))
    story.append(Paragraph("MRN: 32165498", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>CHIEF COMPLAINT:</b>", styles['Heading2']))
    story.append(Paragraph("Severe headache for 3 days, associated with nausea and blurred vision", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>HISTORY OF PRESENT ILLNESS:</b>", styles['Heading2']))
    hpi = """Patient reports sudden onset headache 3 days ago described as throbbing, located in bilateral temporal region. 
    Pain is 7/10 in severity. Associated with nausea (no vomiting), photophobia, and blurry vision. 
    No history of migraines. No recent head trauma. No fever or neck stiffness. 
    Tried acetaminophen and ibuprofen with minimal relief. 
    Reports stress at work and poor sleep recently."""
    story.append(Paragraph(hpi, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>PAST MEDICAL HISTORY:</b>", styles['Heading2']))
    story.append(Paragraph("- Hypertension (diagnosed 2023)", styles['Normal']))
    story.append(Paragraph("- No diabetes", styles['Normal']))
    story.append(Paragraph("- No prior surgeries", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>MEDICATIONS:</b>", styles['Heading2']))
    story.append(Paragraph("- Lisinopril 10mg daily", styles['Normal']))
    story.append(Paragraph("- Ibuprofen PRN", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>VITAL SIGNS:</b>", styles['Heading2']))
    story.append(Paragraph("BP: 142/88 mmHg", styles['Normal']))
    story.append(Paragraph("HR: 92 bpm", styles['Normal']))
    story.append(Paragraph("Temp: 98.4°F", styles['Normal']))
    story.append(Paragraph("RR: 18/min", styles['Normal']))
    story.append(Paragraph("O2 Sat: 98%", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>PHYSICAL EXAM:</b>", styles['Heading2']))
    exam = """General: Alert and oriented, mild distress due to headache
    Head/Neck: Normocephalic, atraumatic. No nuchal rigidity.
    Neurological: Cranial nerves II-XII intact. Pupils equal and reactive to light. No focal deficits.
    Cardiovascular: Regular rate and rhythm, no murmurs"""
    story.append(Paragraph(exam, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>ASSESSMENT/DIAGNOSIS:</b>", styles['Heading2']))
    story.append(Paragraph("1. Severe tension-type headache vs migraine", styles['Normal']))
    story.append(Paragraph("2. Hypertension - poorly controlled", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>TREATMENT PLAN:</b>", styles['Heading2']))
    plan = """1. Prescribed Sumatriptan 50mg for acute headache
    2. Increased Lisinopril to 20mg daily for BP control
    3. Recommended stress reduction and sleep hygiene
    4. Follow-up in 2 weeks to reassess BP and headache control
    5. If headache worsens or vision changes, go to ED immediately"""
    story.append(Paragraph(plan, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

if __name__ == "__main__":
    print("Generating sample medical documents...")
    print("=" * 50)
    
    create_discharge_summary()
    create_referral_letter()
    create_insurance_auth()
    create_lab_report()
    create_general_visit()
    
    print("=" * 50)
    print("✅ All sample documents created in 'sample_documents' folder!")
    print("\nDocuments created:")
    print("1. discharge_summary.pdf - Hospital discharge summary")
    print("2. referral_letter.pdf - Neurology referral letter")
    print("3. insurance_authorization.pdf - Prior authorization request")
    print("4. lab_report.pdf - Laboratory results with abnormalities")
    print("5. general_visit.pdf - General outpatient visit note")