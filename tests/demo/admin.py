from django.contrib import admin
from .models import Book, Author, Category
from django.contrib.admin.options import ModelAdmin, TabularInline,\
    InlineModelAdmin
from django.forms.forms import Form
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import BaseInlineFormSet

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)

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
    
class BookInline(InlineModelAdmin):
    template="websheets/admin_inline.html"
    model=Book
    
    def get_css_width(self):
        return "100%";
    
    def get_css_height(self):
        return "10em"
    
    def get_formset(self, request, obj=None, **kwargs):
        return formset_factory(WebSheetForm, WebSheetFormSet)
    
@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    inlines=(BookInline,)
    model=Author