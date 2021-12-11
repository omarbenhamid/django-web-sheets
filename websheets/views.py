from django.views.generic.base import TemplateView


class WebSheetView(TemplateView):
    template_name="websheets/spreadsheet.html"
    resource_class=None