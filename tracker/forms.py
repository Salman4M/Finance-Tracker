from django import forms


from tracker.models import Asset,Alert



class BuyAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['symbol', 'amount']


class AlertForm(forms.ModelForm):
    class Meta:
        model=Alert
        fields=['condition','asset','target_price']


