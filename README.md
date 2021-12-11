# Django Web Sheets

Web Sheets is a simple module to allow editing models on an online spreadsheet. 
It is meant to be pythonic and simple. It is based on the excelent 
[django import export](https://github.com/django-import-export/django-import-export)
resource system.

## Getting started

1. Install the module with PIP
2. Insure you add 'websheets' to your settings.py :
```python
INSTALLED_APPS = [
    ...
    'websheets',
    ...
]

```
2. Create some models, we use the Book / Category / Author model 
   from (Django Import Export Documentation](https://django-import-export.readthedocs.io/en/stable/getting_started.html)
3. Create a View sublcassing `websheets.views.WebSheetsView`

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

