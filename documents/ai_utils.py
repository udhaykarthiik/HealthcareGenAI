"""
AI Utilities for Healthcare Document Processing
Uses Groq LLM via LangChain for medical document analysis
"""

import os
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
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable


# ─────────────────────────────────────────────────────────────────────────────
#  Colour palette
# ─────────────────────────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#003366")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
WHITE      = colors.white
TEXT_DARK  = colors.HexColor("#1A1A1A")
TEXT_GREY  = colors.HexColor("#555555")


# ─────────────────────────────────────────────────────────────────────────────
#  Custom Flowable: full-width blue section header bar
# ─────────────────────────────────────────────────────────────────────────────
class SectionHeaderBar(Flowable):
    """Renders a filled dark-blue bar with white bold header text."""

    def __init__(self, text, height=22):
        super().__init__()
        self._text   = text
        self._height = height
        self._width  = 0  # resolved in wrap()

    def wrap(self, available_width, available_height):
        self._width = available_width
        return available_width, self._height

    def draw(self):
        c = self.canv
        c.setFillColor(DARK_BLUE)
        c.rect(0, 0, self._width, self._height, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(8, 6, self._text.upper())


# ─────────────────────────────────────────────────────────────────────────────
#  Paragraph style factory
# ─────────────────────────────────────────────────────────────────────────────
def _build_styles() -> dict:
    base = getSampleStyleSheet()

    def s(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "doc_title": s(
            "doc_title",
            fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=2,
        ),
        "doc_subtitle": s(
            "doc_subtitle",
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=TEXT_GREY, alignment=TA_CENTER, spaceAfter=4,
        ),
        "sub_heading": s(
            "sub_heading",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=DARK_BLUE, spaceBefore=8, spaceAfter=3,
        ),
        "body": s(
            "body",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=TEXT_DARK, spaceAfter=4,
        ),
        "body_justify": s(
            "body_justify",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=TEXT_DARK, spaceAfter=4, alignment=TA_JUSTIFY,
        ),
        "bullet": s(
            "bullet",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=TEXT_DARK, leftIndent=16, spaceAfter=2,
        ),
        "numbered": s(
            "numbered",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=TEXT_DARK, leftIndent=20, firstLineIndent=-14, spaceAfter=2,
        ),
        "label": s(
            "label",
            fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=DARK_BLUE,
        ),
        "value": s(
            "value",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=TEXT_DARK,
        ),
        "footer": s(
            "footer",
            fontName="Helvetica-Oblique", fontSize=7, leading=10,
            textColor=TEXT_GREY, alignment=TA_CENTER,
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Text helpers
# ─────────────────────────────────────────────────────────────────────────────
def _clean_markdown(text: str) -> str:
    """Strip all markdown symbols from AI-generated text."""
    if not text:
        return ""
    text = str(text)
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _xml_escape(text: str) -> str:
    """Escape characters that break ReportLab's XML Paragraph parser."""
    if not text:
        return ""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def _safe_para(text: str, style) -> Paragraph:
    return Paragraph(_xml_escape(str(text or "Not mentioned")), style)


# ─────────────────────────────────────────────────────────────────────────────
#  Footer callback (called by ReportLab on every page)
# ─────────────────────────────────────────────────────────────────────────────
def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.setFillColor(TEXT_GREY)
    canvas.drawCentredString(
        doc.pagesize[0] / 2, 0.40 * inch,
        "CONFIDENTIAL – This document contains protected health information (PHI). "
        "Unauthorised disclosure is strictly prohibited.",
    )
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(
        doc.pagesize[0] - 0.75 * inch, 0.40 * inch,
        f"Page {doc.page}",
    )
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
#  Patient info 2-column table
# ─────────────────────────────────────────────────────────────────────────────
def _patient_info_table(entities: dict, styles: dict) -> Table:
    pi = entities.get("patient_info", {})

    def row(label, value):
        return [
            Paragraph(label, styles["label"]),
            Paragraph(_xml_escape(str(value or "Not mentioned")), styles["value"]),
        ]

    if isinstance(pi, dict):
        data = [
            row("Patient Name:", pi.get("name", "Not mentioned")),
            row("Age:",           pi.get("age",  "Not mentioned")),
            row("Gender:",        pi.get("gender", "Not mentioned")),
            row("MRN / ID:",      pi.get("ID", pi.get("id", "Not mentioned"))),
        ]
    else:
        lines = [l.strip() for l in str(pi).split("\n") if l.strip()]
        data = [[Paragraph("", styles["label"]),
                 Paragraph(_xml_escape(l), styles["value"])] for l in lines]
        if not data:
            data = [[Paragraph("", styles["label"]),
                     Paragraph("Not mentioned", styles["value"])]]

    tbl = Table(data, colWidths=[1.5 * inch, 5.0 * inch], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN",           (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",       (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",    (0, 0), (-1, -1), 4),
        ("LEFTPADDING",      (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS",   (0, 0), (-1, -1), [LIGHT_BLUE, WHITE]),
    ]))
    return tbl


# ─────────────────────────────────────────────────────────────────────────────
#  List builders
# ─────────────────────────────────────────────────────────────────────────────
def _bullet_paragraphs(text, styles: dict) -> list:
    """
    Convert a string or list into bullet-point Paragraph flowables.
    Handles: plain string, newline-separated string, Python list.
    """
    # Normalise to list of strings
    if isinstance(text, list):
        items = [str(i) for i in text if str(i).strip()]
    else:
        raw = str(text or "").strip()
        if not raw or raw == "Not mentioned":
            return [_safe_para("Not mentioned", styles["body"])]
        items = [l.strip() for l in raw.split("\n") if l.strip()]

    if not items:
        return [_safe_para("Not mentioned", styles["body"])]

    result = []
    for item in items:
        # strip any existing bullet / dash prefix
        item = re.sub(r"^[•\-\*]\s*", "", item)
        result.append(Paragraph(f"• {_xml_escape(item)}", styles["bullet"]))
    return result


def _medications_paragraphs(meds, styles: dict) -> list:
    """
    Format medications list. Each entry may be a dict {name, dosage, frequency}
    or a plain string.
    """
    if not meds or str(meds).strip() in ("", "Not mentioned"):
        return [_safe_para("Not mentioned", styles["body"])]

    if isinstance(meds, list):
        items = meds
    else:
        # plain string – treat line-by-line as bullets
        return _bullet_paragraphs(meds, styles)

    result = []
    for med in items:
        if isinstance(med, dict):
            name  = med.get("name", med.get("medication", "Unknown"))
            dose  = med.get("dosage", "")
            freq  = med.get("frequency", "")
            parts = [name]
            if dose: parts.append(dose)
            if freq: parts.append(f"— {freq}")
            line  = " ".join(parts)
        else:
            line = str(med)
        line = re.sub(r"^[•\-\*]\s*", "", line.strip())
        result.append(Paragraph(f"• {_xml_escape(line)}", styles["bullet"]))

    return result or [_safe_para("Not mentioned", styles["body"])]


def _numbered_paragraphs(text: str, styles: dict) -> list:
    """
    Convert plain-text numbered summary into properly indented Paragraphs.
    Lines that start with a digit+dot are indented; others are plain body text.
    """
    if not text or text.strip() == "Not mentioned":
        return [_safe_para("Not mentioned", styles["body"])]

    lines = [l.strip() for l in str(text).split("\n") if l.strip()]
    result = []
    for line in lines:
        if re.match(r"^\d+[\.\)]\s", line):
            result.append(Paragraph(_xml_escape(line), styles["numbered"]))
        else:
            result.append(Paragraph(_xml_escape(line), styles["body"]))
    return result or [_safe_para("Not mentioned", styles["body"])]


# ─────────────────────────────────────────────────────────────────────────────
#  Section wrapper
# ─────────────────────────────────────────────────────────────────────────────
def _section(title: str, content_flowables: list, bottom_space: float = 0.10) -> list:
    """Header bar + content + bottom spacer, kept together where possible."""
    block = (
        [Spacer(1, 4), SectionHeaderBar(title), Spacer(1, 6)]
        + content_flowables
        + [Spacer(1, bottom_space * inch)]
    )
    return block


def _sub(title: str, styles: dict) -> Paragraph:
    return Paragraph(title, styles["sub_heading"])


# ─────────────────────────────────────────────────────────────────────────────
#  SOAPNoteGenerator
# ─────────────────────────────────────────────────────────────────────────────
class SOAPNoteGenerator:
    """Generate a professional two-page SOAP note PDF."""

    @staticmethod
    def generate_soap_pdf(
        document_data: Dict,
        summary_text: str,
        entities: Dict,
    ) -> BytesIO:
        """
        Build and return a BytesIO PDF buffer.

        Parameters
        ----------
        document_data : dict  – filename, uploaded_at, user
        summary_text  : str   – AI clinical summary (may contain markdown)
        entities      : dict  – structured medical entities
        """
        pdf_buffer = BytesIO()
        styles = _build_styles()
        margin = 0.75 * inch

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin + 0.25 * inch,
            title="SOAP Medical Note",
            author="Healthcare AI System",
        )

        story = []

        # ── Document title bar ─────────────────────────────────────────
        story.append(Paragraph("SOAP NOTE — Clinical Documentation", styles["doc_title"]))
        story.append(Paragraph(
            f"Document: {document_data.get('filename', 'Unknown')}  |  "
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  |  "
            f"Prepared by: {document_data.get('user', 'System')}",
            styles["doc_subtitle"],
        ))
        story.append(HRFlowable(
            width="100%", thickness=1.5, color=DARK_BLUE,
            spaceBefore=2, spaceAfter=10,
        ))

        # ── 1. PATIENT INFORMATION ─────────────────────────────────────
        story += _section(
            "Patient Information",
            [_patient_info_table(entities, styles)],
        )

        # ── 2. SUBJECTIVE ─────────────────────────────────────────────
        story += _section(
            "Subjective — Patient Report",
            [
                _sub("Chief Complaint", styles),
                _safe_para(entities.get("chief_complaint", "Not mentioned"), styles["body"]),
                _sub("Current Symptoms", styles),
                *_bullet_paragraphs(entities.get("symptoms", "Not mentioned"), styles),
            ],
        )

        # ── 3. OBJECTIVE ──────────────────────────────────────────────
        vitals = entities.get("vitals", "Not mentioned")
        if isinstance(vitals, dict):
            vitals_text = "\n".join(
                f"{k.replace('_', ' ').title()}: {v}" for k, v in vitals.items()
            )
        else:
            vitals_text = str(vitals)

        story += _section(
            "Objective — Clinical Findings",
            [
                _sub("Vital Signs", styles),
                *_bullet_paragraphs(vitals_text, styles),
                _sub("Physical Examination / Findings", styles),
                _safe_para(
                    entities.get("examination", "Refer to source document for full examination details."),
                    styles["body"],
                ),
            ],
        )

        # ── 4. ASSESSMENT ─────────────────────────────────────────────
        story += _section(
            "Assessment — Clinical Impression",
            [
                _sub("Primary Diagnosis", styles),
                *_bullet_paragraphs(entities.get("diagnosis", "Not mentioned"), styles),
            ],
        )

        # ── 5. PLAN ───────────────────────────────────────────────────
        story += _section(
            "Plan — Treatment and Follow-up",
            [
                _sub("Treatment Plan", styles),
                *_bullet_paragraphs(entities.get("treatment_plan", "Not mentioned"), styles),
                _sub("Medications Prescribed", styles),
                *_medications_paragraphs(entities.get("medications", "Not mentioned"), styles),
            ],
        )

        # ── PAGE 2: Complete Clinical Summary ─────────────────────────
        story.append(PageBreak())

        story.append(Paragraph("SOAP NOTE — Clinical Documentation", styles["doc_title"]))
        story.append(HRFlowable(
            width="100%", thickness=1.5, color=DARK_BLUE,
            spaceBefore=2, spaceAfter=10,
        ))

        clean_summary = _clean_markdown(summary_text)

        story += _section(
            "Complete Clinical Summary",
            _numbered_paragraphs(clean_summary, styles),
            bottom_space=0.20,
        )

        # ── Build PDF ─────────────────────────────────────────────────
        doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
        pdf_buffer.seek(0)
        return pdf_buffer

    # Legacy alias
    @staticmethod
    def _clean_text(text: str) -> str:
        return _clean_markdown(text)


# ─────────────────────────────────────────────────────────────────────────────
#  DocumentProcessor
# ─────────────────────────────────────────────────────────────────────────────
class DocumentProcessor:
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
        return "OCR functionality coming soon. Upload PDF documents for now."


# ─────────────────────────────────────────────────────────────────────────────
#  MedicalAIAssistant
# ─────────────────────────────────────────────────────────────────────────────
class MedicalAIAssistant:
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
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a medical AI assistant analyzing clinical documents.
Extract the following information. If absent, use "Not mentioned".

Return ONLY a JSON object with these keys:
- patient_info: dict with keys name, age, gender, ID
- chief_complaint: string
- symptoms: list of strings
- diagnosis: list of strings
- medications: list of dicts with keys name, dosage, frequency
- treatment_plan: list of strings
- vitals: dict of vital sign name -> value
- examination: string (physical exam findings)

Medical Document:
{text}

JSON Output:""",
        )
        try:
            return (prompt | self.llm | parser).invoke({"text": text[:4000]})
        except Exception as e:
            print(f"⚠️ Entity extraction error: {str(e)}")
            return {k: "Not extracted" for k in [
                "patient_info", "chief_complaint", "symptoms", "diagnosis",
                "medications", "treatment_plan", "vitals", "examination",
            ]}

    def generate_summary(self, text: str, document_type: str = "medical") -> str:
        prompt = PromptTemplate(
            input_variables=["document_type", "text"],
            template="""You are an expert medical documentation assistant.
Generate a professional summary of this {document_type} document.
Use plain numbered sections (1. 2. 3.). Do NOT use markdown symbols.

Medical Document:
{text}

Professional Medical Summary:""",
        )
        try:
            return (prompt | self.llm).invoke(
                {"document_type": document_type, "text": text[:5000]}
            ).content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_discharge_summary(self, text: str) -> str:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Generate a professional discharge summary with numbered plain-text sections.
Do NOT use markdown. Source:\n{text}\n\nDischarge Summary:""",
        )
        try:
            return (prompt | self.llm).invoke({"text": text[:5000]}).content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_referral_letter(self, text: str) -> str:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Generate a professional referral letter with numbered plain-text sections.
Do NOT use markdown. Source:\n{text}\n\nReferral Letter:""",
        )
        try:
            return (prompt | self.llm).invoke({"text": text[:5000]}).content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_insurance_authorization(self, text: str) -> str:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Generate a prior authorization request with numbered plain-text sections.
Do NOT use markdown. Source:\n{text}\n\nPrior Authorization Request:""",
        )
        try:
            return (prompt | self.llm).invoke({"text": text[:5000]}).content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_lab_report_summary(self, text: str) -> str:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""Summarise the lab report in numbered plain-text sections.
Do NOT use markdown. Source:\n{text}\n\nLab Report Summary:""",
        )
        try:
            return (prompt | self.llm).invoke({"text": text[:5000]}).content.strip()
        except Exception as e:
            return f"Error: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
#  AgentOrchestrator
# ─────────────────────────────────────────────────────────────────────────────
class AgentOrchestrator:
    def __init__(self):
        self.assistant = MedicalAIAssistant()
        self.processor = DocumentProcessor()

    def process_document(self, file_path: str, file_type: str, doc_type: str = "general") -> Dict:
        results = {"status": "processing", "extracted_text": "", "entities": {}, "summary": "", "error": None}
        try:
            if file_type.lower() == "pdf":
                results["extracted_text"] = self.processor.extract_text_from_pdf(file_path)
            elif file_type.lower() in ["jpg", "jpeg", "png"]:
                results["extracted_text"] = self.processor.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")

            if not results["extracted_text"]:
                raise Exception("No text could be extracted from document")

            results["entities"] = self.assistant.extract_medical_entities(results["extracted_text"])

            dispatch = {
                "discharge":  self.assistant.generate_discharge_summary,
                "referral":   self.assistant.generate_referral_letter,
                "insurance":  self.assistant.generate_insurance_authorization,
                "lab_report": self.assistant.generate_lab_report_summary,
            }
            fn = dispatch.get(doc_type, lambda t: self.assistant.generate_summary(t, doc_type))
            results["summary"] = fn(results["extracted_text"])
            results["status"] = "completed"
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
        return results