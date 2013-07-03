# coding: utf-8
from django.contrib import admin
from classifier.models import ClassifierCategory, Document

class ClassifierCategoryAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ['id','categoryName', 'yes']
    list_filter = []
    readonly_fields = []


class DocumentAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ['id','corpus', 'corpusHash']
    list_filter = []
    readonly_fields = []

admin.register(ClassifierCategory, ClassifierCategoryAdmin)
admin.register(Document, DocumentAdmin)
