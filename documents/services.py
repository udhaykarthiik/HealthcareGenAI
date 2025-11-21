from django.utils import timezone
from .models import Document, Summary
from .ai_utils import AgentOrchestrator


class DocumentProcessingService:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()

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
