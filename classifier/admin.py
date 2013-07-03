# coding: utf-8
from django.contrib import admin


class MailAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ['id','author','recipient','email','title','body','time','force']
    list_filter = []
    readonly_fields = []
    raw_id_fields = ['recipient', 'author']
