"""Django admin for AI Engine app."""
from django.contrib import admin
from .models import PromptTemplate, SemanticCache

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'organization', 'is_public', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['name', 'template']

@admin.register(SemanticCache)
class SemanticCacheAdmin(admin.ModelAdmin):
    list_display = ['model', 'hit_count', 'last_hit_at', 'expires_at', 'created_at']
    list_filter = ['model', 'expires_at']
    readonly_fields = ['prompt_hash', 'hit_count', 'last_hit_at']
