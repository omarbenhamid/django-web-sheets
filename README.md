# Django Web Sheets

Web Sheets is a simple module to allow editing models on an online spreadsheet. 
It is meant to be pythonic and simple. It is based on the excelent 
[django import export](https://github.com/django-import-export/django-import-export)
resource system.

## Getting started

1. Install the module with PIP
2. Create some models, suppose you have Book model
3. Create a View sublcassing WebSheetsView

```python
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
```

3. Add it to url.py 
```
   path('test1/', MySheetView.as_view()),
``` 

And you're done. For advanced users it is interesting to override `get_sheet_resource_classes`
to create sheets dynamically and `get_queryset(sheetname)` to fine tune what
data shows in each sheet.

