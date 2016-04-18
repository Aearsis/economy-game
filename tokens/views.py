import random
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect

from core.models import InvalidTransaction
from ekonomicka.utils import team_required, game_running_required
from tokens.models import Token, TokenUnusableException


class TokenForm(forms.Form):
    code = forms.CharField(min_length=Token.LENGTH, max_length=Token.LENGTH, label="Kód lístečku:")

@team_required
@game_running_required
def token_input(request):
    if request.method == 'POST':
        try:
            f = TokenForm(request.POST)
            if f.is_valid():
                token = Token.get(f.cleaned_data['code'])
                token.use(request.team)
                messages.add_message(request, messages.SUCCESS, "Našel jsi %s!" % token.entity)
                return redirect("token:input")
        except Token.DoesNotExist:
            messages.add_message(request, messages.INFO, "Takový lísteček neexistuje!")
        except (InvalidTransaction, TokenUnusableException) as e:
            messages.add_message(request, messages.WARNING, "%s" % e)
    else:
        f = TokenForm()

    return render(request, "tokens/input.html", {'form': f})

@permission_required("game_control")
def token_print(request):
    tok = list(Token.objects.all())
    random.shuffle(tok)
    return render(request, "tokens/print.html", {
        'tokens': tok
    })