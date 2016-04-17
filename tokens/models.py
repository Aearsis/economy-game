import string

import random

import timedelta
from django.core import validators
from django.db import models, transaction

from core.models import Entity, Team, Transaction, Status, Game


class Token(models.Model):
    LENGTH = 6
    CONSONANTS="QWRTPSDFGHJKLZXCVBNM"
    VOWELS="AEIOUY"

    code = models.CharField(max_length=LENGTH, validators=[
        validators.RegexValidator("([%s][%s]){%d}[%s]{%d}" % (CONSONANTS, VOWELS, LENGTH / 2, CONSONANTS, LENGTH % 2))],
                            primary_key=True)
    entity = models.ForeignKey(Entity)
    used_by = models.ForeignKey(Team, null=True, blank=True, default=None)
    used_time = timedelta.TimedeltaField(null=True, blank=True, default=None)

    @property
    def value(self):
        return 1

    @transaction.atomic
    def _use_commit(self, team):
        # You can't simply add to balance, as there may be some constraints (e.g. licences)
        with Transaction() as t:
            t.add(team, self.entity, self.value)

        self.used_by = team
        self.used_time = Game.game_time()
        self.save()

    def use(self, team: Team):
        if self.used_by is not None:
            if self.used_by == team:
                raise TokenUnusableException("Tento kód už jsi použil.")
            else:
                Status.add("Tým %s přinesl kód, který už použil tým %s. Mají co vysvětlovat!" % (team, self.used_by), Status.DANGER, self.used_by)
                raise TokenUnusableException("Tento kód už použil tým %s. Myslím, že je čas zajít za organizátory!" % self.used_by)

        return self._use_commit(team)

    @staticmethod
    def get(code: str):
        return Token.objects.get(code=code.upper())

    @staticmethod
    def randomcode():
        return "".join(random.choice(Token.VOWELS if i % 2 == 1 else Token.CONSONANTS) for i in range(Token.LENGTH))

    @staticmethod
    def generate_one(entity: Entity):
        t = Token(entity=entity, code=Token.randomcode())
        t.save()
        return t

    def __repr__(self):
        return "<Token: %s>" % self.code

class TokenUnusableException(Exception):
    pass