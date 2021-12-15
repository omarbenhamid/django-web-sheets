from django.views.generic.base import TemplateView
import json
from django.http.response import HttpResponseNotAllowed, JsonResponse
import tablib
from django.utils.functional import cached_property
from collections import OrderedDict
from import_export.resources import Resource
from inspect import isclass
import logging
import types

logger = logging.getLogger(__name__)


class WebSheetView(TemplateView):
    template_name="websheets/spreadsheet.html"
    sheet_resource_classes=[] #List of class or tuple ("sheetName","class")
    allow_save=True
    delete_empty_rows=False #Delete rows that contain only ids
    hide_id_col=False #Hide or keep id visible
    
    def __hook_apply_delete_empty_rows(self, res_instance):
        if hasattr(res_instance, '__hooked__'): return
        tmp = res_instance.for_delete
        
        def for_delete(self, row, instance):
            if tmp(row,instance): return True
            idfields=res_instance.get_import_id_fields()
            for f,v in row.items():
                if f not in idfields and v != '': return False
            return True
        res_instance.for_delete = types.MethodType(for_delete, res_instance)
        res_instance.__hooked__ = True

    
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
    
    def handle_missing_sheet_onsave(self, sheetname, resource):
        """ Handle the case where a sheet is absent on save """
        pass
    
    def get_sheet_format(self, sheetname):
        """
        Override this to return a DICT of format options for the sheet (compliant with
        x-spreadsheet)
        """
        pass
    
    def update_sheet_format(self, sheetname, formatjson):
        """
        Override this when new sheet format is received for update. This usually 
        boils down to saving the data somehow.
        """
        pass
    
    @cached_property
    def _sheet_resources(self):
        return self._get_sheet_resources()
    
    def _get_sheet_resources(self):
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
        return OrderedDict((name, {
            'data': res.export(self.get_queryset(name, res)).csv,
            'format': self.get_sheet_format(name) or {}
        })
                for name, res in sheet_resources.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #FixME: support multisheet (one qs per sheet)
        context['json'] = json.dumps(self._get_sheets_json())
        context['allow_save'] = "true" if self.get_allow_save() else "false";
        context['hide_id_col'] = "true" if self.hide_id_col else "false";
        return context

    def post(self, *args, **kwargs):
        if not self.get_allow_save():
            return HttpResponseNotAllowed(['GET'])

        errors={}
        sheet_resources=dict(self._sheet_resources)
        sheet_data=dict((k[8:],v) for k,v in self.request.POST.items()\
            if k.startswith('__data__'))
        sheet_formats=dict((k[10:],v) for k,v in self.request.POST.items()\
            if k.startswith('__format__'))
        
        for k,v in sheet_data.items():
            res=sheet_resources.get(k,None)
            if not res:
                res=self.get_resource_for_new_sheet(k)
                if not res: 
                    errors[k]={1:["Unknown sheet %s" % k]}
                    continue
                else:
                    sheet_resources[k]=res
            if self.delete_empty_rows:
                self.__hook_apply_delete_empty_rows(res)
            
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
            if result.has_validation_errors():
                if k not in errors:
                    errors[k]={}
                for ir in result.invalid_rows:
                    rownum=ir.number
                    if rownum not in errors[k]: errors[k][rownum]=[]
                    for ek,ev in ir.error.message_dict.items():
                        for em in ev:
                            errors[k][rownum].append("%s: %s" % (ek,em))
            

        if not errors:
            for k,v in sheet_data.items():
                ds=tablib.import_set(v, format='csv')
                sheet_resources[k].import_data(ds, dry_run=False)
            for k,v in self._sheet_resources.items():
                if k not in sheet_data.keys():
                    self.handle_missing_sheet_onsave(k, v)
            for k,v in sheet_formats.items():
                try:
                    fjson=json.loads(v)
                except:
                    logger.warn("Ignoring misformatted format string")
                    logger.debug("Traceback:", exc_info=True)
                    continue
                self.update_sheet_format(k, fjson)
            return JsonResponse(self._get_sheets_json(self._get_sheet_resources()))
        else:
            return JsonResponse(errors, status=500)

