from django.contrib import admin
from .models import Portfolio, Transactions

class PortfolioAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['profile_image'].widget.attrs['class'] = 'cloudinary-field'
        return form

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('profile_image') is None:
            obj.profile_image = None
        super().save_model(request, obj, form, change)

admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Transactions)