import string

import random
from django.core import validators
from django.db import models, transaction

from core.models import Entity, Team, Transaction


class Token(models.Model):
    LENGTH = 6
    CHARS = string.ascii_uppercase

    code = models.CharField(max_length=LENGTH, validators=[validators.RegexValidator("[%s]{%d}" % (CHARS, LENGTH))],
                            primary_key=True)
    entity = models.ForeignKey(Entity)
    used = models.BooleanField(default=False)

    @property
    def value(self):
        return 1

    @transaction.atomic
    def use(self, team: Team):
        if self.used:
            raise TokenUnusableException("Tento kód už byl použit.")

        # You can't simply add to balance, as there may be some constraints (e.g. licences)
        with Transaction() as t:
            t.add(team, self.entity, self.value)

        self.used = True
        self.save()

    @staticmethod
    def get(code: str):
        return Token.objects.get(code.upper())

    @staticmethod
    def generate_one(entity: Entity):
        code = "".join(random.choice(Token.CHARS) for _ in range(Token.LENGTH))
        t = Token(entity=entity, code=code)
        t.save()
        return t

    def __repr__(self):
        return "<Token: %s>" % self.code

class TokenUnusableException(Exception):
    pass