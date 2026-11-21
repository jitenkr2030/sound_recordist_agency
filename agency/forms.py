from django import forms
from . import models

class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"

class LeadForm(StyledModelForm):
    class Meta:
        model = models.Lead
        fields = ["name","organisation","email","phone","requirement","source"]
class AudioAssetForm(StyledModelForm):
    class Meta:
        model = models.AudioAsset
        fields = ["project","session","title","file","version","is_client_visible","description"]
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
