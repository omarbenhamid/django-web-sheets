from django.views.generic.base import TemplateView
import json


class WebSheetView(TemplateView):
    template_name="websheets/spreadsheet.html"
    resource_class=None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        res=self.resource_class()
        
        #FixME: support multisheet (one qs per sheet)
        context['json'] = json.dumps({"sheet 0": res.export().csv})
        return context