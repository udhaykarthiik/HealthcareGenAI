from django.utils import timezone
from django.http import FileResponse
from .models import Document, Summary
from .ai_utils import AgentOrchestrator, SOAPNoteGenerator
from datetime import datetime


class DocumentProcessingService:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.soap_generator = SOAPNoteGenerator()

    def process_uploaded_document(self, document_id: int, doc_type: str = "general") -> bool:
        """
        Processes an uploaded document using AI pipelines.

        Args:
            document_id (int): ID of the Document object
            doc_type (str): Type of document (general, discharge, referral, etc.)

        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            document = Document.objects.get(id=document_id)
            document.status = 'processing'
            document.save()

            # Extract file path and type
            file_path = document.file.path
            file_type = document.file_type or 'pdf'

            # Call AI orchestrator with doc_type parameter
            results = self.orchestrator.process_document(file_path, file_type, doc_type)

            if results["status"] == "completed":
                document.extracted_text = results["extracted_text"]
                document.status = 'completed'
                document.processed_at = timezone.now()
                document.save()

                # Save summary in DB
                Summary.objects.create(
                    document=document,
                    summary_text=results["summary"],
                    extracted_entities=results["entities"],
                    model_used="gemini-2.0-flash",
                    confidence_score=0.85
                )
                return True
            else:
                document.status = 'failed'
                document.save()
                return False

        except Exception as e:
            print(f"❌ Service error: {str(e)}")
            try:
                document = Document.objects.get(id=document_id)
                document.status = 'failed'
                document.save()
            except:
                pass
            return False

    def generate_soap_pdf(self, document_id: int) -> FileResponse:
        """Generate downloadable SOAP note PDF"""
        
        try:
            document = Document.objects.get(id=document_id)
            summary = Summary.objects.get(document=document)
            
            # Prepare document data
            doc_data = {
                'filename': document.original_filename,
                'upload_date': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Generate PDF
            pdf_buffer = self.soap_generator.generate_soap_pdf(
                doc_data,
                summary.summary_text,
                summary.extracted_entities
            )
            
            # Create file response
            filename = f"SOAP_Note_{document.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response = FileResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            raise Exception(f"Error generating SOAP PDF: {str(e)}")
