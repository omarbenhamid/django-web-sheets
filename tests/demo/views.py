from websheets.views import WebSheetView
from import_export.resources import ModelResource
from demo.models import Book

class BookResource(ModelResource):

    class Meta:
        model = Book

class MySheetView(WebSheetView):
    resource_class=BookResource