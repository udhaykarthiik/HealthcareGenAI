"""
AI Utilities for Healthcare Document Processing
Uses Google Gemini 2.0 Flash via LangChain for medical document analysis
"""

import os
from typing import Dict
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


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
    AI Assistant for medical document analysis leveraging Gemini 2.0 Flash model.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is missing")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        )
        print("✅ Gemini 2.0 Flash initialized successfully!")

    def extract_medical_entities(self, text: str) -> Dict:
        response_schemas = [
            ResponseSchema(name="patient_info", description="Patient demographic information (name, age, gender, ID)"),
            ResponseSchema(name="chief_complaint", description="Main reason for visit or primary symptoms"),
            ResponseSchema(name="symptoms", description="List of symptoms mentioned in the document"),
            ResponseSchema(name="diagnosis", description="Medical diagnosis or provisional diagnosis"),
            ResponseSchema(name="medications", description="Prescribed medications with dosage if mentioned"),
            ResponseSchema(name="treatment_plan", description="Treatment recommendations and follow-up instructions"),
            ResponseSchema(name="vitals", description="Vital signs if mentioned (BP, pulse, temperature, etc.)"),
        ]

        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()

        entity_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical AI assistant analyzing clinical documents.
Extract the following information from the medical document below.
If any information is not present, write "Not mentioned".

{format_instructions}

Medical Document:
{text}

Output:""",
            partial_variables={"format_instructions": format_instructions},
        )

        chain = LLMChain(llm=self.llm, prompt=entity_prompt)

        try:
            response = chain.invoke({"text": text[:4000]})
            parsed_output = output_parser.parse(response["text"])
            return parsed_output
        except Exception as e:
            print(f"⚠️ Entity extraction error: {str(e)}")
            return {schema.name: "Not extracted" for schema in response_schemas}

    def generate_summary(self, text: str, document_type: str = "medical") -> str:
        summary_prompt = PromptTemplate(
            input_variables=["document_type", "text"],
            template="""You are an expert medical documentation assistant.
Generate a clear, professional summary of this {document_type} document.

**Instructions:**
- Write in clear medical terminology
- Organize information logically (Patient Info → Chief Complaint → Diagnosis → Treatment)
- Be concise but comprehensive
- Highlight critical information
- Use bullet points for lists
- Include medication names and dosages accurately

**Medical Document:**
{text}

**Professional Medical Summary:**""",
        )

        chain = LLMChain(llm=self.llm, prompt=summary_prompt)

        try:
            response = chain.invoke({"document_type": document_type, "text": text[:5000]})
            return response["text"].strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_discharge_summary(self, text: str) -> str:
        discharge_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a hospital discharge summary generator.
Create a professional discharge summary with these sections:

**DISCHARGE SUMMARY**

**1. PATIENT INFORMATION**
[Extract patient demographics]

**2. ADMISSION DATE & DISCHARGE DATE**
[Extract dates if available]

**3. PRINCIPAL DIAGNOSIS**
[Main diagnosis]

**4. HOSPITAL COURSE**
[Brief narrative of treatment received]

**5. MEDICATIONS AT DISCHARGE**
[List medications with dosage]

**6. DISCHARGE INSTRUCTIONS**
[Follow-up care, activity restrictions, diet]

**7. FOLLOW-UP**
[Appointment information]

---

**Source Document:**
{text}

**Generate Discharge Summary:**""",
        )

        chain = LLMChain(llm=self.llm, prompt=discharge_prompt)

        try:
            response = chain.invoke({"text": text[:5000]})
            return response["text"].strip()
        except Exception as e:
            return f"Error generating discharge summary: {str(e)}"

    def generate_referral_letter(self, text: str) -> str:
        """
        Generate a professional referral letter from medical document text.
        
        Args:
            text: Raw document text
            
        Returns:
            Formatted referral letter
        """
        
        referral_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical referral letter processor.
Create a professional referral letter with these sections:

**REFERRAL LETTER**

**1. REFERRING PHYSICIAN INFORMATION**
[Extract referring doctor's name, specialty, contact]

**2. PATIENT INFORMATION**
[Patient demographics and identification]

**3. DATE OF REFERRAL**
[Extract date if available]

**4. REASON FOR REFERRAL**
[Primary reason patient is being referred]

**5. RELEVANT MEDICAL HISTORY**
[Past medical history, current conditions, medications]

**6. CLINICAL FINDINGS**
[Physical exam findings, test results, symptoms]

**7. SPECIALIST REQUESTED**
[Type of specialist needed - cardiology, orthopedics, etc.]

**8. URGENCY LEVEL**
[Routine, urgent, or emergency referral]

**9. SPECIFIC QUESTIONS/REQUESTS**
[What the referring physician wants addressed]

---

**Source Document:**
{text}

**Generate Referral Letter:**"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=referral_prompt)
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response["text"].strip()
        except Exception as e:
            return f"Error generating referral letter: {str(e)}"

    def generate_insurance_authorization(self, text: str) -> str:
        """
        Generate structured insurance prior authorization from medical document.
        
        Args:
            text: Raw document text
            
        Returns:
            Formatted insurance authorization summary
        """
        
        authorization_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are an insurance prior authorization specialist.
Create a structured prior authorization request with these sections:

**PRIOR AUTHORIZATION REQUEST**

**1. PATIENT INFORMATION**
[Patient name, DOB, insurance ID, policy number]

**2. PROVIDER INFORMATION**
[Requesting physician name, NPI number, specialty, contact]

**3. REQUESTED SERVICE/PROCEDURE**
[Specific procedure, treatment, or medication requested]

**4. DIAGNOSIS CODES (ICD-10)**
[Primary and secondary diagnosis codes with descriptions]

**5. PROCEDURE CODES (CPT/HCPCS)**
[Relevant procedure codes for requested service]

**6. CLINICAL JUSTIFICATION**
[Medical necessity, why this treatment is required]

**7. SUPPORTING DOCUMENTATION**
[Lab results, imaging, previous treatments tried]

**8. URGENCY LEVEL**
[Standard, expedited, or emergency authorization needed]

**9. DURATION OF APPROVAL REQUESTED**
[Time period or number of treatments/sessions]

**10. ALTERNATIVE TREATMENTS CONSIDERED**
[Other options tried or reasons why alternatives are unsuitable]

---

**Source Document:**
{text}

**Generate Prior Authorization Request:**"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=authorization_prompt)
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response["text"].strip()
        except Exception as e:
            return f"Error generating insurance authorization: {str(e)}"

    def generate_lab_report_summary(self, text: str) -> str:
        """
        Generate clinical summary of lab reports for physician consultations.
        
        Args:
            text: Raw lab report text
            
        Returns:
            Formatted lab report summary
        """
        
        lab_report_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a clinical laboratory specialist summarizing lab reports for physician consultations.
Create a clear lab report summary with these sections:

**LABORATORY REPORT SUMMARY**

**1. PATIENT INFORMATION**
[Patient name, age, gender, medical record number]

**2. TEST DATE & COLLECTION TIME**
[When specimens were collected]

**3. ORDERING PHYSICIAN**
[Physician who ordered the tests]

**4. TESTS PERFORMED**
[List of all laboratory tests conducted]

**5. CRITICAL/ABNORMAL FINDINGS**
[Highlight any values outside normal ranges - use ⚠️ for critical values]

**6. NORMAL FINDINGS**
[Results within normal reference ranges]

**7. CLINICAL SIGNIFICANCE**
[Interpretation of what abnormal results may indicate]

**8. TRENDING (if applicable)**
[Comparison with previous results if mentioned]

**9. RECOMMENDATIONS**
[Suggested follow-up tests or clinical actions]

**10. REFERENCE RANGES**
[Include normal ranges for key tests]

---

**Source Lab Report:**
{text}

**Generate Lab Report Summary:**"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=lab_report_prompt)
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response["text"].strip()
        except Exception as e:
            return f"Error generating lab report summary: {str(e)}"


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
