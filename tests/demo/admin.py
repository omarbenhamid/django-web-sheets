from django.contrib import admin
from .models import Book, Author, Category
from websheets.admin import WebSheetInlineModelAdmin
from django.contrib.admin.options import ModelAdmin

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)


class BookInline(WebSheetInlineModelAdmin):
    model=Book
    
    
@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    inlines=(BookInline,)
    model=Author