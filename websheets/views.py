from django.views.generic.base import TemplateView
import json
from django.http.response import HttpResponseNotAllowed, JsonResponse
import tablib


class WebSheetView(TemplateView):
    template_name="websheets/spreadsheet.html"
    resource_class=None
    allow_save=True

    def _get_sheets_json(self, res=None):
        if not res: res=self.resource_class()
        return {"sheet 0": res.export().csv};

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #FixME: support multisheet (one qs per sheet)
        context['json'] = json.dumps(self._get_sheets_json())
        context['allow_save'] = "true" if self.allow_save else "false";
        return context

    def post(self, *args, **kwargs):
        if not self.allow_save:
            return HttpResponseNotAllowed(['GET'])

        res=self.resource_class()

        errors={}
        for k,v in self.request.POST.items():
            ds=tablib.import_set(v, format='csv')
            result=res.import_data(ds, dry_run=True)
            if result.has_errors():
                if result.base_errors:
                    raise Exception("Internal errors during import")
                if k not in errors:
                    errors[k]={}

                for rownum, errs in result.row_errors():
                    if rownum not in errors[k]: errors[k][rownum]=[]
                    for e in errs:
                        if hasattr(e.error, '__iter__'):
                            errors[k][rownum].extend(str(p) for p in e.error)
                        else:
                            errors[k][rownum].append(str(e.error))

        if not errors:
            for k,v in self.request.POST.items():
                ds=tablib.import_set(v, format='csv')
                res.import_data(ds, dry_run=False)
            
            return JsonResponse(self._get_sheets_json(res))
        else:
            return JsonResponse(errors, status=500)

