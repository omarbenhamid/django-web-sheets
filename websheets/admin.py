from django.contrib import admin
from django.contrib.admin.options import ModelAdmin, InlineModelAdmin
from django.forms.forms import Form
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.db.models.base import Model
from import_export.resources import ModelResource, modelresource_factory,\
    ModelDeclarativeMetaclass
from django.utils.functional import cached_property
import tablib
from websheets.core import collect_import_errors
import json

# Register your models here.

class WebSheetForm(Form):
    pass

class WebSheetFormSet(BaseFormSet):
    def __init__(self, **kwargs):
        self.instance=kwargs.pop('instance')
        self.queryset=kwargs.pop('queryset')
        if 'save_as_new' in kwargs: 
            kwargs.pop('save_as_new')
        
        self.new_objects=[]
        self.changed_objects=[]
        BaseFormSet.__init__(self, **kwargs) #data, files, auto_id, prefix, initial, error_class, form_kwargs)
    
    
    def _modelresource_factory(self, model, resource_class, extra_exclude=None):
        """
        Factory for creating ``ModelResource`` class for given Django model.
        """
        
            
            
        attrs = {'model': model}
        basemeta=getattr(resource_class, 'Meta', object)
        if extra_exclude:
            exclude=list(getattr(basemeta,'exclude',()))
            exclude.extend(extra_exclude)
            attrs['exclude']=exclude
        
        Meta = type(str('Meta'), (basemeta,), attrs)
    
        class_name = model.__name__ + str('Resource')
    
        class_attrs = {
            'Meta': Meta,
        }
    
        metaclass = ModelDeclarativeMetaclass
        Clazz = metaclass(class_name, (resource_class,), class_attrs)
        
        #Override before save instance to set the right fj
        orig_bsi=Clazz.before_save_instance
        def new_bsi(_self, instance, *args, **kwargs):
            #Force FK to the right value.
            setattr(instance, self.fk.name, self.instance)
            if instance.pk: self.changed_objects.append((instance, []))
            else: self.new_objects.append(instance)
            return orig_bsi(_self, instance, *args, **kwargs)
        Clazz.before_save_instance=new_bsi
        
        return Clazz

    @cached_property
    def resource(self):
        return self._modelresource_factory(self.inline.model, self.inline.resource_class, [self.fk.name])()
    
    def is_valid(self):
        ds=tablib.import_set(self.data[self.prefix+'-csvdata'], 
                             format='csv')
        result=self.resource.import_data(ds, dry_run=True)
        
        if not ( result.has_errors() or result.has_validation_errors() ):
            self.valid_dataset=ds
            return True
        self.import_errors=collect_import_errors(result)
        return False
    
    def import_errors_json(self):
        if hasattr(self, 'import_errors'):
            return json.dumps(self.import_errors)
        else:
            return ''
    
    def save(self):
        #DElete first not to systematically delete new createions
        delete_qs=self._queryset().exclude(id__in=[int(id) for id in
                                         self.valid_dataset.get_col(self.valid_dataset.headers.index('id')) 
                                         if id ])
        self.deleted_objects=list(delete_qs.all())
        delete_qs.delete()
        
        self.resource.import_data(self.valid_dataset, dry_run=False)
        
    

    def get_queryset(self):
        #This is none to avoid creating the forms for instances.
        return self.queryset.none()
    
    def _queryset(self):
        return self.queryset.filter(**{self.fk.name: self.instance})
    
    def ascsv(self):
        return self.resource.export(self._queryset()).csv
    
    def csvdata(self):
        """Return submitted data or newly load if not submited"""
        key=self.prefix+'-csvdata'
        if self.data and key in self.data:
            return self.data[key]
        else:
            return self.ascsv()
    
class Undef(Model):
    class meta:
        proxy = True
    



    
class WebSheetInlineModelAdmin(InlineModelAdmin):
    """
        Set at least resource_class or model
        if resource_class is set, make sure to exclude the FK to parent ...
    """
    template="websheets/admin_inline.html"
    resource_class=None
    model=Undef
    css_height="15em"
    spreadsheet_format={} #Todo use this as json
       
    def __init__(self, parent_model, admin_site):
        if self.model == Undef:
            if self.resource_class:
                self.model=self.resource_class._meta.model
            else:
                raise Exception("Bad config of WebSheetInlineModelAdmin: either set model or resource class")
        
        if not self.resource_class:
            self.resource_class=ModelResource
            
        InlineModelAdmin.__init__(self, parent_model, admin_site)
        
        self.FormSet = inlineformset_factory(self.parent_model, self.model, formset=WebSheetFormSet,
                                     form=WebSheetForm, fields=[])
        self.FormSet.inline=self
    
    
    
    def get_css_height(self):
        return self.css_height
    

    def get_formset(self, request, obj=None, **kwargs):
        return self.FormSet
    
    