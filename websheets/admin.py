from django.contrib import admin
from django.contrib.admin.options import ModelAdmin, InlineModelAdmin
from django.forms.forms import Form
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseInlineFormSet

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
        self.new_objects=[]
        self.changed_objects=[]
        self.deleted_objects=[]
    
    @classmethod
    def get_default_prefix(cls):
        #TODO: models.inlineformset_factory look at jow it is done
        return "TODO-deduce-me-from-fk-as"

    def get_queryset(self):
        return self.queryset.none()
    
    
class WebSheetInlineModelAdmin(InlineModelAdmin):
    template="websheets/admin_inline.html"
    
    def get_css_height(self):
        return "15em"
    
    def get_formset(self, request, obj=None, **kwargs):
        FormSet=formset_factory(WebSheetForm, WebSheetFormSet)
        FormSet.inline=self
        return FormSet
    