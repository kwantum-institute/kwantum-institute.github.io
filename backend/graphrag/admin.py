from django.contrib import admin

from .models import Chunk, GraphEdge, GraphNode, ProvenanceEntry

admin.site.register(GraphNode)
admin.site.register(GraphEdge)
admin.site.register(Chunk)
admin.site.register(ProvenanceEntry)
