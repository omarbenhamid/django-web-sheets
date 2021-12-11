from websheets.views import WebSheetView
from import_export.resources import ModelResource
from demo.models import Book, Category

class BookResource(ModelResource):

    class Meta:
        model = Book

class CategoryResource(ModelResource):

    class Meta:
        model = Category

class MySheetView(WebSheetView):
    sheet_resource_classes=[("Books",BookResource),
                            ("Cateogories", CategoryResource)]