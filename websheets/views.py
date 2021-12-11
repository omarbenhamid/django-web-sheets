from django.views.generic.base import TemplateView
import json
from django.http.response import HttpResponseNotAllowed, JsonResponse
import tablib
from django.utils.functional import cached_property
from collections import OrderedDict
from import_export.resources import Resource
from inspect import isclass


class WebSheetView(TemplateView):
    template_name="websheets/spreadsheet.html"
    sheet_resource_classes=[] #List of class or tuple ("sheetName","class")
    allow_save=True
    
    def get_sheet_resource_classes(self):
        return self.sheet_resource_classes
    
    def get_queryset(self, sheetname, resource):
        return resource.get_queryset()
    
    @cached_property
    def _sheet_resources(self):
        ret=OrderedDict()
        for rc in self.get_sheet_resource_classes():
            if isclass(rc) and issubclass(rc, Resource): #This is a resource class
                ret[rc.__name__]=rc()
            if hasattr(rc, '__len__') and len(rc) == 2:
                n,c=rc
                ret[n]=c()
            else:
                raise Exception("sheet_resource_classes can be either a Resource class or (name,ResourceClass) tuple")
        return ret

    def _get_sheets_json(self):
        return OrderedDict((name, res.export().csv)
                for name, res in self._sheet_resources.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #FixME: support multisheet (one qs per sheet)
        context['json'] = json.dumps(self._get_sheets_json())
        context['allow_save'] = "true" if self.allow_save else "false";
        return context

    def post(self, *args, **kwargs):
        if not self.allow_save:
            return HttpResponseNotAllowed(['GET'])

        errors={}
        for k,v in self.request.POST.items():
            res=self._sheet_resources[k]
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
                self._sheet_resources[k].import_data(ds, dry_run=False)
            
            return JsonResponse(self._get_sheets_json())
        else:
            return JsonResponse(errors, status=500)

