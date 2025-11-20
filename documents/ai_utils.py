"""
AI Utilities for Healthcare Document Processing
Uses Google Gemini via LangChain for medical document analysis
"""

import os
from typing import Dict, List, Optional
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json


class DocumentProcessor:
    """
    Handles document text extraction from various formats
    """
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            
            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """
        Extract text from image using OCR (placeholder for future)
        
        Args:
            file_path: Path to image file
            
        Returns:
            Extracted text as string
        """
        # TODO: Implement OCR with Tesseract or EasyOCR
        # For now, return placeholder
        return "OCR functionality coming soon. Upload PDF documents for now."


class MedicalAIAssistant:
    """
    AI Assistant for medical document analysis using Gemini Pro
    """
    
    def __init__(self):
        """Initialize Gemini model via LangChain"""
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Initialize Gemini Pro model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.3,  # Lower = more focused, Higher = more creative
            convert_system_message_to_human=True
        )
        
        print("✅ Gemini Pro initialized successfully!")
    
    def extract_medical_entities(self, text: str) -> Dict:
        """
        Extract structured medical entities from document text
        
        Args:
            text: Raw document text
            
        Returns:
            Dictionary with extracted entities (symptoms, diagnosis, medications, etc.)
        """
        
        # Define expected output structure
        response_schemas = [
            ResponseSchema(
                name="patient_info",
                description="Patient demographic information (name, age, gender, ID)"
            ),
            ResponseSchema(
                name="chief_complaint",
                description="Main reason for visit or primary symptoms"
            ),
            ResponseSchema(
                name="symptoms",
                description="List of symptoms mentioned in the document"
            ),
            ResponseSchema(
                name="diagnosis",
                description="Medical diagnosis or provisional diagnosis"
            ),
            ResponseSchema(
                name="medications",
                description="Prescribed medications with dosage if mentioned"
            ),
            ResponseSchema(
                name="treatment_plan",
                description="Treatment recommendations and follow-up instructions"
            ),
            ResponseSchema(
                name="vitals",
                description="Vital signs if mentioned (BP, pulse, temperature, etc.)"
            )
        ]
        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create prompt template
        entity_prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical AI assistant analyzing clinical documents.
Extract the following information from the medical document below.
If any information is not present, write "Not mentioned".

{format_instructions}

Medical Document:
{text}

Output:""",
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Create chain
        chain = LLMChain(llm=self.llm, prompt=entity_prompt)
        
        try:
            # Get response
            response = chain.invoke({"text": text[:4000]})  # Limit input to avoid token limits
            
            # Parse structured output
            parsed_output = output_parser.parse(response['text'])
            return parsed_output
        
        except Exception as e:
            print(f"⚠️ Entity extraction error: {str(e)}")
            # Return fallback structure
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
        """
        Generate comprehensive medical summary from document text
        
        Args:
            text: Raw document text
            document_type: Type of document (discharge, consultation, etc.)
            
        Returns:
            AI-generated summary as string
        """
        
        # Create summary prompt template
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

**Professional Medical Summary:**"""
        )
        
        # Create chain
        chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        
        try:
            # Generate summary (limit input to 5000 chars to avoid token limits)
            response = chain.invoke({
                "document_type": document_type,
                "text": text[:5000]
            })
            
            return response['text'].strip()
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_discharge_summary(self, text: str) -> str:
        """
        Generate formatted discharge summary specifically
        
        Args:
            text: Raw document text
            
        Returns:
            Formatted discharge summary
        """
        
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

**Generate Discharge Summary:**"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=discharge_prompt)
        
        try:
            response = chain.invoke({"text": text[:5000]})
            return response['text'].strip()
        
        except Exception as e:
            return f"Error generating discharge summary: {str(e)}"


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents for complex document processing
    This demonstrates multi-agent architecture for the hackathon
    """
    
    def __init__(self):
        """Initialize the orchestrator with AI assistant"""
        self.assistant = MedicalAIAssistant()
        self.processor = DocumentProcessor()
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        """
        Complete document processing pipeline
        
        Args:
            file_path: Path to uploaded file
            file_type: File extension (pdf, jpg, etc.)
            
        Returns:
            Dictionary with all processing results
        """
        
        results = {
            "status": "processing",
            "extracted_text": "",
            "entities": {},
            "summary": "",
            "error": None
        }
        
        try:
            # Step 1: Extract text based on file type
            print(f"📄 Step 1: Extracting text from {file_type} file...")
            
            if file_type.lower() == 'pdf':
                results["extracted_text"] = self.processor.extract_text_from_pdf(file_path)
            elif file_type.lower() in ['jpg', 'jpeg', 'png']:
                results["extracted_text"] = self.processor.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
            
            if not results["extracted_text"]:
                raise Exception("No text could be extracted from document")
            
            print(f"✅ Extracted {len(results['extracted_text'])} characters")
            
            # Step 2: Extract medical entities (Agent 1)
            print("🔍 Step 2: Extracting medical entities...")
            results["entities"] = self.assistant.extract_medical_entities(
                results["extracted_text"]
            )
            print("✅ Entities extracted")
            
            # Step 3: Generate summary (Agent 2)
            print("📝 Step 3: Generating AI summary...")
            results["summary"] = self.assistant.generate_summary(
                results["extracted_text"]
            )
            print("✅ Summary generated")
            
            results["status"] = "completed"
            return results
        
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"❌ Processing failed: {str(e)}")
            return results
