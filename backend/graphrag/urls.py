from django.urls import path

from . import views

app_name = "graphrag"

urlpatterns = [
    path("nodes/", views.NodeListView.as_view(), name="node-list"),
    path("nodes/<str:pk>/", views.NodeDetailView.as_view(), name="node-detail"),
    path("edges/", views.EdgeListView.as_view(), name="edge-list"),
    path("edges/<str:pk>/", views.EdgeDetailView.as_view(), name="edge-detail"),
    path("search/", views.SemanticSearchView.as_view(), name="semantic-search"),
    path("batch/", views.BatchImportView.as_view(), name="batch-import"),
    path("mermaid/", views.MermaidExportView.as_view(), name="mermaid-export"),
    path("provenance/", views.ProvenanceListView.as_view(), name="provenance-list"),
    path("research/", views.ResearchView.as_view(), name="research"),
    path("architecture/", views.ArchitectureView.as_view(), name="architecture"),
    path("tune/", views.TuneView.as_view(), name="tune"),
]
