from django.contrib import admin
from .models import Tier, Size, Image, Profile, TemporaryLink
from django import forms


admin.site.register(Size)
admin.site.register(Image)
admin.site.register(Profile)
admin.site.register(TemporaryLink)


class TierAdminForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the queryset for thumbnail_sizes field to display only Sizes added by admin
        self.fields['thumbnail_sizes'].queryset = Size.objects.filter(thumbnail_size=True)

class TierAdmin(admin.ModelAdmin):
    form = TierAdminForm

admin.site.register(Tier, TierAdmin)
