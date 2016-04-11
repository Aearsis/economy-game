from django import forms

from auctions.models import *


class AuctionedItemForm(forms.ModelForm):
    class Meta:
        model = AuctionedItem
        fields = ['entity']
        labels = {
            'entity': ""
        }

    coef = forms.ChoiceField(choices=(
        (1, "nabízíme"),
        (-1, "požadujeme"),
    ), label="")
    amount = forms.IntegerField(label="")


class CreateAuctionForm(forms.ModelForm):
    ALLOWED_TIMESPANS = (
        (60, "1 minuta"),
        (180, "3 minuty"),
        (300, "5 minut"),
        (600, "10 minut"),
    )

    class Meta:
        model = WhiteAuction
        fields = ['description', 'var_entity', 'var_step', 'var_min']
        labels = {
            'description': 'Popis aukce',
            'var_step': 'Minimální příhoz'
        }

    timespan = forms.ChoiceField(label="Délka aukce", choices=ALLOWED_TIMESPANS)

    var_direction = forms.ChoiceField(choices=(
        (1, "požaduji nejméně"),
        (-1, "nabízím nejvýše"),
    ), label="Druh aukce")


class BidForm(forms.Form):
    bid = forms.IntegerField(min_value=0, label="Hodnota příhozu")
    coef = forms.IntegerField(widget=forms.HiddenInput(), required=True, initial=1)