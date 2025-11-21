import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcore.settings')
django.setup()

from documents.services import DocumentProcessingService
from documents.models import Document

def test_all_document_types():
    """Test all 4 document processing types (excluding OCR)"""
    
    service = DocumentProcessingService()
    doc = Document.objects.first()
    
    if not doc:
        print("No documents found. Upload a document first.")
        return
    
    print(f"\nTesting with document: {doc.original_filename}\n")
    
    # Test 1: Discharge Summary
    print("=" * 60)
    print("TEST 1: DISCHARGE SUMMARY")
    print("=" * 60)
    doc.status = 'pending'
    doc.save()
    result1 = service.process_uploaded_document(doc.id, doc_type="discharge")
    print(f"Result: {'SUCCESS' if result1 else 'FAILED'}\n")
    
    # Test 2: Referral Letter
    print("=" * 60)
    print("TEST 2: REFERRAL LETTER")
    print("=" * 60)
    doc.status = 'pending'
    doc.save()
    result2 = service.process_uploaded_document(doc.id, doc_type="referral")
    print(f"Result: {'SUCCESS' if result2 else 'FAILED'}\n")
    
    # Test 3: Insurance Authorization
    print("=" * 60)
    print("TEST 3: INSURANCE AUTHORIZATION")
    print("=" * 60)
    doc.status = 'pending'
    doc.save()
    result3 = service.process_uploaded_document(doc.id, doc_type="insurance")
    print(f"Result: {'SUCCESS' if result3 else 'FAILED'}\n")
    
    # Test 4: Lab Report Summary
    print("=" * 60)
    print("TEST 4: LAB REPORT SUMMARY")
    print("=" * 60)
    doc.status = 'pending'
    doc.save()
    result4 = service.process_uploaded_document(doc.id, doc_type="lab_report")
    print(f"Result: {'SUCCESS' if result4 else 'FAILED'}\n")
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total = 4
    passed = sum([result1, result2, result3, result4])
    print(f"Tests Passed: {passed}/{total}")
    print("=" * 60)
    
    print(f"\nView results at: http://127.0.0.1:8000/documents/")

if __name__ == "__main__":
    test_all_document_types()
