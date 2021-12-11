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
    
    def get_allow_save(self):
        return self.allow_save
    
    def get_sheet_resource_classes(self):
        """ Return a list, each item can be :
         a resource class
         a resource instance
         a tuple (Sheet title, resource class)
         a tuple (Sheet title, resource instance)
        """
        return self.sheet_resource_classes
    
    def get_queryset(self, sheetname, resource):
        return resource.get_queryset()
    
    def get_resource_for_new_sheet(self, sheetname):
        """ Called when a new sheet is encountred in import 
        must return the resource instance for this new shset or None if
        creation is not supported
        """
        return None
    @cached_property
    def _sheet_resources(self):
        ret=OrderedDict()
        for rc in self.get_sheet_resource_classes():
            if hasattr(rc, '__len__') and len(rc) == 2:
                n,c=rc
            else:
                n=None
                c=rc
            
            if isclass(c) and issubclass(c, Resource): #This is a resource class
                if not n: 
                    n=c.__name__
                c=c()
            elif isinstance(c, Resource):
                if not n: 
                    n=c.__class__.__name__
            else:
                raise Exception("sheet_resource_classes can be either a Resource class or instance or (name,ResourceClass or instance) tuple")
            ret[n]=c
            
        return ret

    def _get_sheets_json(self, sheet_resources=None):
        if not sheet_resources: sheet_resources=self._sheet_resources
        return OrderedDict((name, res.export(self.get_queryset(name, res)).csv)
                for name, res in sheet_resources.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #FixME: support multisheet (one qs per sheet)
        context['json'] = json.dumps(self._get_sheets_json())
        context['allow_save'] = "true" if self.get_allow_save() else "false";
        return context

    def post(self, *args, **kwargs):
        if not self.get_allow_save():
            return HttpResponseNotAllowed(['GET'])

        errors={}
        sheet_resources=dict(self._sheet_resources)
        for k,v in self.request.POST.items():
            res=sheet_resources.get(k,None)
            if not res:
                res=self.get_resource_for_new_sheet(k)
                if not res: 
                    errors[k]={1:["Unknown sheet %s" % k]}
                    continue
                else:
                    sheet_resources[k]=res
                
            ds=tablib.import_set(v, format='csv')
            result=res.import_data(ds, dry_run=True)
            if result.has_errors():
                if k not in errors:
                    errors[k]={}
                    
                if result.base_errors:
                    errors[k][1]=["Internal base errors"]
                
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
                sheet_resources[k].import_data(ds, dry_run=False)
            
            return JsonResponse(self._get_sheets_json(sheet_resources))
        else:
            return JsonResponse(errors, status=500)

