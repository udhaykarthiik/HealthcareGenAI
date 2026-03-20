from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponse
from django.contrib import messages
from .models import Document
from .ai_utils import AgentOrchestrator, SOAPNoteGenerator
import os
import re
from datetime import datetime
from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
#  Text helpers
# ─────────────────────────────────────────────────────────────────────────────
def clean_markdown(text: str) -> str:
    """Remove all markdown formatting symbols from text."""
    if not text:
        return text
    text = str(text)
    # Bold / italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"_{1,2}(.*?)_{1,2}",   r"\1", text, flags=re.DOTALL)
    # Headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Inline code
    text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text, flags=re.DOTALL)
    # Horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _str(value, fallback="Not mentioned") -> str:
    """Safe string coercion with fallback."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


# ─────────────────────────────────────────────────────────────────────────────
#  Entity formatter  (used by download_soap_pdf before passing to SOAPNoteGenerator)
# ─────────────────────────────────────────────────────────────────────────────
def _format_entities_for_pdf(entities: Dict) -> Dict:
    """
    Normalise raw AI-extracted entities into the shapes that
    SOAPNoteGenerator's helper functions expect:

      patient_info   → dict  {name, age, gender, ID}   OR plain string
      chief_complaint→ string
      symptoms       → list[str]   (SOAPNoteGenerator will bullet-ify)
      diagnosis      → list[str]
      medications    → list[dict{name,dosage,frequency}] OR list[str]
      treatment_plan → list[str]
      vitals         → dict{sign: value}  OR plain string
      examination    → string
    """
    fmt = {}

    # ── patient_info ──────────────────────────────────────────────────
    pi = entities.get("patient_info", {})
    if isinstance(pi, dict):
        fmt["patient_info"] = {
            "name":   _str(pi.get("name")),
            "age":    _str(pi.get("age")),
            "gender": _str(pi.get("gender")),
            "ID":     _str(pi.get("ID", pi.get("id", pi.get("mrn", "Not mentioned")))),
        }
    else:
        fmt["patient_info"] = _str(pi)

    # ── chief complaint ───────────────────────────────────────────────
    fmt["chief_complaint"] = _str(entities.get("chief_complaint"))

    # ── symptoms  (normalise to list[str]) ────────────────────────────
    fmt["symptoms"] = _to_str_list(entities.get("symptoms"))

    # ── diagnosis (normalise to list[str]) ────────────────────────────
    fmt["diagnosis"] = _to_str_list(entities.get("diagnosis"))

    # ── medications ───────────────────────────────────────────────────
    meds = entities.get("medications")
    if isinstance(meds, list):
        clean_meds = []
        for m in meds:
            if isinstance(m, dict):
                clean_meds.append({
                    "name":      _str(m.get("name", m.get("medication", "Unknown"))),
                    "dosage":    _str(m.get("dosage", ""), ""),
                    "frequency": _str(m.get("frequency", m.get("freq", "")), ""),
                })
            else:
                clean_meds.append({"name": _str(m), "dosage": "", "frequency": ""})
        fmt["medications"] = clean_meds
    else:
        # plain string – leave as-is; SOAPNoteGenerator handles strings too
        fmt["medications"] = _str(meds)

    # ── treatment plan (normalise to list[str]) ───────────────────────
    fmt["treatment_plan"] = _to_str_list(entities.get("treatment_plan"))

    # ── vitals ────────────────────────────────────────────────────────
    vitals = entities.get("vitals")
    if isinstance(vitals, dict):
        fmt["vitals"] = {k: _str(v) for k, v in vitals.items()}
    else:
        fmt["vitals"] = _str(vitals)

    # ── examination (physical findings) ───────────────────────────────
    fmt["examination"] = _str(entities.get("examination",
                              entities.get("physical_examination",
                              entities.get("findings", ""))))

    return fmt


def _to_str_list(value) -> list:
    """Convert any value to a clean list of non-empty strings."""
    if isinstance(value, list):
        return [_str(i) for i in value if _str(i) != "Not mentioned" or len(value) == 1]
    raw = _str(value)
    if raw == "Not mentioned":
        return ["Not mentioned"]
    # newline- or semicolon-separated plain strings
    items = [l.strip() for l in re.split(r"[\n;]", raw) if l.strip()]
    return items if items else ["Not mentioned"]


# ─────────────────────────────────────────────────────────────────────────────
#  AI orchestrator (module-level singleton)
# ─────────────────────────────────────────────────────────────────────────────
orchestrator = AgentOrchestrator()


# ─────────────────────────────────────────────────────────────────────────────
#  Auth views
# ─────────────────────────────────────────────────────────────────────────────
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("home")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            f"Welcome {user.username}! Your account has been created successfully.",
        )
        return response


# ─────────────────────────────────────────────────────────────────────────────
#  General views
# ─────────────────────────────────────────────────────────────────────────────
def home(request):
    return render(request, "home.html")


@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "documents/document_list.html", {"documents": documents})


@login_required
def upload_document(request):
    if request.method == "POST":
        file     = request.FILES.get("file")
        doc_type = request.POST.get("doc_type", "general")

        if not file:
            messages.error(request, "No file selected.")
            return redirect("upload_document")

        file_extension = file.name.split(".")[-1].lower()
        if file_extension not in ["pdf", "jpg", "jpeg", "png"]:
            messages.error(
                request,
                "Unsupported file type. Please upload PDF, JPG, or PNG files.",
            )
            return redirect("upload_document")

        document = Document.objects.create(
            user=request.user,
            file=file,
            document_type=doc_type,
            filename=file.name,
            file_type=file_extension,
        )

        try:
            result = orchestrator.process_document(document.file.path, file_extension, doc_type)

            if result["status"] == "completed":
                document.extracted_text = result["extracted_text"]
                document.entities       = result["entities"]
                document.ai_summary     = result["summary"]
                document.status         = "completed"
                document.save()
                messages.success(request, "Document processed successfully!")
                return redirect("summary_detail", document_id=document.id)
            else:
                document.status        = "failed"
                document.error_message = result.get("error", "Unknown error")
                document.save()
                messages.error(request, f"Processing failed: {result.get('error', 'Unknown error')}")
                return redirect("document_list")

        except Exception as e:
            document.status        = "failed"
            document.error_message = str(e)
            document.save()
            messages.error(request, f"Error processing document: {str(e)}")
            return redirect("document_list")

    return render(request, "documents/upload.html")


@login_required
def summary_detail(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)

    if document.status != "completed":
        messages.warning(request, "Document processing not completed yet.")
        return redirect("document_list")

    entities       = document.entities if isinstance(document.entities, dict) else {}
    cleaned_summary = clean_markdown(document.ai_summary)

    context = {
        "document":    document,
        "entities":    entities,
        "summary":     cleaned_summary,
        "upload_date": document.uploaded_at,
    }
    return render(request, "documents/summary_detail.html", context)


# ─────────────────────────────────────────────────────────────────────────────
#  PDF download
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def download_soap_pdf(request, document_id):
    """Generate and stream a professional SOAP note PDF."""
    document = get_object_or_404(Document, id=document_id, user=request.user)

    if document.status != "completed":
        messages.error(request, "Document not processed yet.")
        return redirect("document_list")

    try:
        # 1. Clean summary text (strip any residual markdown)
        cleaned_summary = clean_markdown(document.ai_summary)

        # 2. Build document metadata dict
        document_data = {
            "filename":    document.filename,
            "uploaded_at": document.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user":        document.user.username,
        }

        # 3. Normalise entities for the PDF generator
        raw_entities = document.entities if isinstance(document.entities, dict) else {}
        formatted_entities = _format_entities_for_pdf(raw_entities)

        # 4. Generate PDF
        pdf_buffer = SOAPNoteGenerator.generate_soap_pdf(
            document_data=document_data,
            summary_text=cleaned_summary,
            entities=formatted_entities,
        )

        # 5. Stream response
        response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="soap_note_{document.id}.pdf"'
        )
        return response

    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect("summary_detail", document_id=document.id)