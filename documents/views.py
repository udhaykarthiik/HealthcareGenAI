from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DocumentUploadForm
from .models import Document
from .services import DocumentProcessingService
import markdown2


def home(request):
    """Landing page for the application"""
    return render(request, 'documents/home.html')

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.info(request, "Document uploaded. Processing will begin soon.")

            # Trigger AI processing (sync for now; consider async for production)
            service = DocumentProcessingService()
            service.process_uploaded_document(doc.id)

            return redirect('document_list')
    else:
        form = DocumentUploadForm()
    return render(request, 'documents/upload.html', {'form': form})


@login_required
def document_list(request):
    docs = Document.objects.filter(user=request.user)
    return render(request, 'documents/list.html', {'docs': docs})


@login_required
@login_required
def summary_detail(request, document_id):
    doc = get_object_or_404(Document, id=document_id, user=request.user)
    summary = doc.summaries.last()

    summary_html = None
    if summary:
        text = summary.get_final_text()  # Call the method
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        summary_html = markdown2.markdown(text)

    return render(request, 'documents/summary.html', {
        'doc': doc,
        'summary': summary,
        'summary_html': summary_html,
    })

