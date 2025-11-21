from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),  # Home page - list all documents
    path('upload/', views.upload_document, name='upload_document'),
    path('summary/<int:document_id>/', views.summary_detail, name='summary_detail'),
]
