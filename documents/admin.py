"""
AI Utilities for Healthcare Document Processing
Uses Groq LLM via LangChain for medical document analysis
"""

import os
import json
import re
from typing import Dict
from io import BytesIO
from datetime import datetime

from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch


class DocumentProcessor:
    """
    Handles document text extraction from PDFs and images (placeholder for OCR).
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        # TODO: Implement OCR with Tesseract or EasyOCR
        return "OCR functionality coming soon. Upload PDF documents for now."


class MedicalAIAssistant:
    """
    AI Assistant for medical document analysis leveraging Groq LLM.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing")

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            groq_api_key=api_key,
        )
        print("✅ Groq LLM initialized successfully!")

    def extract_medical_entities(self, text: str) -> Dict:
        parser = JsonOutputParser()
        
        entity_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical AI assistant analyzing clinical documents.
Extract the following information from the medical document below.
If any information is not present, write "Not mentioned".

Return a JSON object with these keys:
- patient_info (Patient demographic information: name, age, gender, ID)
- chief_complaint (Main reason for visit or primary symptoms)
- symptoms (List of symptoms mentioned in the document)
- diagnosis (Medical diagnosis or provisional diagnosis)
- medications (Prescribed medications with dosage if mentioned)
- treatment_plan (Treatment recommendations and follow-up instructions)
- vitals (Vital signs if mentioned: BP, pulse, temperature, etc.)

Medical Document:
{text}

JSON Output:""",
        )

        chain = entity_prompt | self.llm | parser

        try:
            response = chain.invoke({"text": text[:4000]})
            return response
        except Exception as e:
            print(f"⚠️ Entity extraction error: {str(e)}")
            return {
                "patient_info": "Not extracted",
                "chief_complaint": "Not extracted",
                "symptoms": "Not extracted",
                "diagnosis": "Not extracted",
                "medications": "Not extracted",
                "treatment_plan": "Not extracted",
                "vitals": "Not extracted"
            }

    def generate_summary(self, text: str, document_type: str = "medical") -> str:
        summary_prompt = PromptTemplate(
            input_variables=["document_type", "text"],
            template="""You are an expert medical documentation assistant.
Generate a clear, professional summary of this {document_type} document.

Instructions:
- Write in clear medical terminology
- Organize information logically (Patient Info → Chief Complaint → Diagnosis → Treatment)
- Be concise but comprehensive
- Highlight critical information
- Use bullet points for lists
- Include medication names and dosages accurately

Medical Document:
{text}

Professional Medical Summary:""",
        )

        chain = summary_prompt | self.llm

        try:
            response = chain.invoke({"document_type": document_type, "text": text[:5000]})
            return response.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_discharge_summary(self, text: str) -> str:
        discharge_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a hospital discharge summary generator.
Create a professional discharge summary with these sections:

DISCHARGE SUMMARY

1. PATIENT INFORMATION
[Extract patient demographics]

2. ADMISSION DATE & DISCHARGE DATE
[Extract dates if available]

3. PRINCIPAL DIAGNOSIS
[Main diagnosis]

4. HOSPITAL COURSE
[Brief narrative of treatment received]

5. MEDICATIONS AT DISCHARGE
[List medications with dosage]

6. DISCHARGE INSTRUCTIONS
[Follow-up care, activity restrictions, diet]

7. FOLLOW-UP
[Appointment information]

---

Source Document:
{text}

Generate Discharge Summary:""",
        )

        chain = discharge_prompt | self.llm

        try:
            response = chain.invoke({"text": text[:5000]})
            return response.content.strip()
        except Exception as e:
            return f"Error generating discharge summary: {str(e)}"

    def generate_referral_letter(self, text: str) -> str:
        referral_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical referral letter processor.
Create a professional referral letter with these sections:

REFERRAL LETTER

1. REFERRING PHYSICIAN INFORMATION
[Extract referring doctor's name, specialty, contact]

2. PATIENT INFORMATION
[Patient demographics and identification]

3. DATE OF REFERRAL
[Extract date if available]

4. REASON FOR REFERRAL
[Primary reason patient is being referred]

5. RELEVANT MEDICAL HISTORY
[Past medical history, current conditions, medications]

6. CLINICAL FINDINGS
[Physical exam findings, test results, symptoms]

7. SPECIALIST REQUESTED
[Type of specialist needed]

8. URGENCY LEVEL
[Routine, urgent, or emergency referral]

9. SPECIFIC QUESTIONS/REQUESTS
[What the referring physician wants addressed]

---

Source Document:
{text}

Generate Referral Letter:"""
        )
        
        chain = referral_prompt | self.llm
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response.content.strip()
        except Exception as e:
            return f"Error generating referral letter: {str(e)}"

    def generate_insurance_authorization(self, text: str) -> str:
        authorization_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are an insurance prior authorization specialist.
Create a structured prior authorization request with these sections:

PRIOR AUTHORIZATION REQUEST

1. PATIENT INFORMATION
[Patient name, DOB, insurance ID, policy number]

2. PROVIDER INFORMATION
[Requesting physician name, NPI number, specialty, contact]

3. REQUESTED SERVICE/PROCEDURE
[Specific procedure, treatment, or medication requested]

4. DIAGNOSIS CODES (ICD-10)
[Primary and secondary diagnosis codes with descriptions]

5. PROCEDURE CODES (CPT/HCPCS)
[Relevant procedure codes for requested service]

6. CLINICAL JUSTIFICATION
[Medical necessity, why this treatment is required]

7. SUPPORTING DOCUMENTATION
[Lab results, imaging, previous treatments tried]

8. URGENCY LEVEL
[Standard, expedited, or emergency authorization needed]

---

Source Document:
{text}

Generate Prior Authorization Request:"""
        )
        
        chain = authorization_prompt | self.llm
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response.content.strip()
        except Exception as e:
            return f"Error generating insurance authorization: {str(e)}"

    def generate_lab_report_summary(self, text: str) -> str:
        lab_report_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a clinical laboratory specialist summarizing lab reports for physician consultations.
Create a clear lab report summary with these sections:

LABORATORY REPORT SUMMARY

1. PATIENT INFORMATION
[Patient name, age, gender, medical record number]

2. TEST DATE & COLLECTION TIME
[When specimens were collected]

3. ORDERING PHYSICIAN
[Physician who ordered the tests]

4. TESTS PERFORMED
[List of all laboratory tests conducted]

5. CRITICAL/ABNORMAL FINDINGS
[Highlight any values outside normal ranges]

6. NORMAL FINDINGS
[Results within normal reference ranges]

7. CLINICAL SIGNIFICANCE
[Interpretation of what abnormal results may indicate]

8. RECOMMENDATIONS
[Suggested follow-up tests or clinical actions]

---

Source Lab Report:
{text}

Generate Lab Report Summary:"""
        )
        
        chain = lab_report_prompt | self.llm
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response.content.strip()
        except Exception as e:
            return f"Error generating lab report summary: {str(e)}"


class SOAPNoteGenerator:
    """Generate professional structured SOAP notes as PDF with proper text wrapping"""
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove markdown and special characters"""
        if not text:
            return "Not mentioned"
        text = str(text)
        text = text.replace('**', '').replace('*', '').replace('##', '').replace('#', '')
        text = text.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        return text.strip()
    
    @staticmethod
    def generate_soap_pdf(document_data: Dict, summary_text: str, entities: Dict) -> BytesIO:
        """Generate a clean, professional SOAP note PDF with blue headers"""
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Main title style
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#003366'),
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        # Blue header style
        header_style = ParagraphStyle(
            'BlueHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#FFFFFF'),
            backColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=8,
            fontName='Helvetica-Bold',
            alignment=0,
            borderPadding=5
        )
        
        # Section heading style
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            fontName='Helvetica'
        )
        
        # Info style for footer
        info_style = ParagraphStyle(
            'InfoText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=8,
            alignment=0
        )
        
        story = []
        
        # TITLE
        story.append(Paragraph("SOAP NOTE - Clinical Documentation", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Document info
        clean_filename = document_data.get('filename', 'Unknown')
        clean_date = datetime.now().strftime('%B %d, %Y at %H:%M')
        story.append(Paragraph(f"Document: {clean_filename}", info_style))
        story.append(Paragraph(f"Generated: {clean_date}", info_style))
        story.append(Spacer(1, 0.2*inch))
        
        # PATIENT INFORMATION (Blue header)
        story.append(Paragraph("PATIENT INFORMATION", header_style))
        patient_info = entities.get('patient_info', 'Not mentioned')
        story.append(Paragraph(patient_info, body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # SUBJECTIVE (Blue header)
        story.append(Paragraph("SUBJECTIVE - Patient Report", header_style))
        
        story.append(Paragraph("Chief Complaint", section_style))
        chief_complaint = entities.get('chief_complaint', 'Not mentioned')
        story.append(Paragraph(chief_complaint, body_style))
        
        story.append(Paragraph("Current Symptoms", section_style))
        symptoms = entities.get('symptoms', 'Not mentioned')
        story.append(Paragraph(symptoms, body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # OBJECTIVE (Blue header)
        story.append(Paragraph("OBJECTIVE - Clinical Findings", header_style))
        
        story.append(Paragraph("Vital Signs", section_style))
        vitals = entities.get('vitals', 'Not mentioned')
        story.append(Paragraph(vitals, body_style))
        
        story.append(Paragraph("Physical Examination Findings", section_style))
        diagnosis = entities.get('diagnosis', 'Not mentioned')
        story.append(Paragraph(diagnosis, body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # ASSESSMENT (Blue header)
        story.append(Paragraph("ASSESSMENT - Clinical Impression", header_style))
        
        story.append(Paragraph("Primary Diagnosis", section_style))
        story.append(Paragraph(diagnosis, body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # PLAN (Blue header)
        story.append(Paragraph("PLAN - Treatment and Follow-up", header_style))
        
        story.append(Paragraph("Treatment Plan", section_style))
        treatment_plan = entities.get('treatment_plan', 'Not mentioned')
        story.append(Paragraph(treatment_plan, body_style))
        
        story.append(Paragraph("Medications Prescribed", section_style))
        medications = entities.get('medications', 'Not mentioned')
        story.append(Paragraph(medications, body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # PAGE BREAK
        story.append(PageBreak())
        
        # COMPLETE CLINICAL SUMMARY (Blue header)
        story.append(Paragraph("COMPLETE CLINICAL SUMMARY", header_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Clean and format the summary
        summary_clean = SOAPNoteGenerator._clean_text(summary_text)
        
        # Format the summary with proper sections
        if summary_clean:
            formatted_summary = summary_clean.replace('**', '').replace('*', '')
            story.append(Paragraph(formatted_summary, body_style))
        else:
            story.append(Paragraph("No summary available", body_style))
        
        # FOOTER
        story.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=1
        )
        footer_text = "CONFIDENTIAL MEDICAL RECORD - Healthcare AI Assistant"
        story.append(Paragraph(footer_text, footer_style))
        story.append(Paragraph("Please review and verify before clinical use", footer_style))
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents for complex document processing based on document type.
    """

    def __init__(self):
        self.assistant = MedicalAIAssistant()
        self.processor = DocumentProcessor()

    def process_document(self, file_path: str, file_type: str, doc_type: str = "general") -> Dict:
        results = {
            "status": "processing",
            "extracted_text": "",
            "entities": {},
            "summary": "",
            "error": None,
        }

        try:
            print(f"📄 Extracting text from {file_type} file...")
            if file_type.lower() == "pdf":
                results["extracted_text"] = self.processor.extract_text_from_pdf(file_path)
            elif file_type.lower() in ["jpg", "jpeg", "png"]:
                results["extracted_text"] = self.processor.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")

            if not results["extracted_text"]:
                raise Exception("No text could be extracted from document")

            print(f"✅ Extracted {len(results['extracted_text'])} characters")

            print(f"🔍 Extracting medical entities...")
            results["entities"] = self.assistant.extract_medical_entities(results["extracted_text"])
            print("✅ Entities extracted")

            print(f"📝 Generating AI summary for document type '{doc_type}'...")
            if doc_type == "discharge":
                results["summary"] = self.assistant.generate_discharge_summary(results["extracted_text"])
            elif doc_type == "referral":
                results["summary"] = self.assistant.generate_referral_letter(results["extracted_text"])
            elif doc_type == "insurance":
                results["summary"] = self.assistant.generate_insurance_authorization(results["extracted_text"])
            elif doc_type == "lab_report":
                results["summary"] = self.assistant.generate_lab_report_summary(results["extracted_text"])
            else:
                results["summary"] = self.assistant.generate_summary(results["extracted_text"], document_type=doc_type)
            print("✅ Summary generated")

            results["status"] = "completed"
            return results

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"❌ Processing failed: {str(e)}")
            return results