from django.contrib import admin
from django.contrib.admin.options import ModelAdmin, InlineModelAdmin
from django.forms.forms import Form
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.db.models.base import Model
from import_export.resources import ModelResource, modelresource_factory

# Register your models here.

class WebSheetForm(Form):
    pass

class WebSheetFormSet(BaseFormSet):
    def __init__(self, **kwargs):
        self.instance=kwargs.pop('instance')
        self.queryset=kwargs.pop('queryset')
        if 'save_as_new' in kwargs: 
            kwargs.pop('save_as_new')
        
        BaseFormSet.__init__(self, **kwargs) #data, files, auto_id, prefix, initial, error_class, form_kwargs)
    
    def save(self):
        #Before import
        # Make sure the attribut fk.name has value instance
        # Identify and delete missing lines
        # Do the import od new lines / updated  lines.
        self.new_objects=[]
        self.changed_objects=[]
        self.deleted_objects=[]
    

    def get_queryset(self):
        #This is none to avoid creating the forms for instances.
        return self.queryset.none()
    
    
    def ascsv(self, sheet_resources=None):
        qs=self.queryset.filter(**{self.fk.name: self.instance})
        return self.inline.resource.export(qs).csv
    
class Undef(Model):
    class meta:
        proxy = True
    
class WebSheetInlineModelAdmin(InlineModelAdmin):
    """
        Set at least resource_class or model
    """
    template="websheets/admin_inline.html"
    resource_class=None
    model=Undef
    css_height="15em"
    spreadsheet_format={} #Todo use this as json
       
    def __init__(self, parent_model, admin_site):
        if self.resource_class:
            if self.model == Undef:
                self.model=self.resource_class._meta.model
                self.resource=self.resource_class()
            else:
                self.resource=modelresource_factory(self.model, self.resource_class)()
            
        if self.model != Undef:
            self.resource=modelresource_factory(self.model)()
        else:
            raise Exception("Bad config of WebSheetInlineModelAdmin: either set model or resource class")

        InlineModelAdmin.__init__(self, parent_model, admin_site)
    
    def get_css_height(self):
        return self.css_height
    
    def get_formset(self, request, obj=None, **kwargs):
        FormSet = inlineformset_factory(self.parent_model, self.model, formset=WebSheetFormSet,
                                     form=WebSheetForm, fields=[])
        #FormSet=formset_factory(WebSheetForm, WebSheetFormSet)
        FormSet.inline=self
        return FormSet
    
    