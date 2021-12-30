from django.contrib import admin
from .models import Book, Author, Category
from websheets.admin import WebSheetInlineModelAdmin
from django.contrib.admin.options import ModelAdmin
from import_export.resources import ModelResource
from demo.models import Papers

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)

class BookResource(ModelResource):
    class Meta:
        model = Book

class BookInline(WebSheetInlineModelAdmin):
    #model=None
    resource_class=BookResource

class PapersInline(WebSheetInlineModelAdmin):
    model=Papers

@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    inlines=(BookInline,PapersInline)
    model=Author