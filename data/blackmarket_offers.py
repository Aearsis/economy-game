
from data.generating import *
from data.blackmarket_statuses import *

from auctions.models import *
from core.models import *

from random import *


def randfloat(a, b):
    assert a <= b
    return a + random.random() * (b - a)


def rand_subset(superset, max_size, min_size=0):
    superset = list(superset)
    size = randint(min_size, max_size)

    if size >= len(superset):
        return set(superset)

    shuffle(superset)
    return set(superset[:size])

def ents():
    return Entity.objects.all()


class EvolvingSetting:
    def __init__(self, setting):
        """setting: list of pairs (percent_time, value) or a dict. In percent_time
        a setting will be changed to value
        """

        self.setting = dict(setting)
        assert 0 in self.setting, 'setting must contain 0 (initial value)'
        assert all(0 <= x <= 1 for x in self.setting.keys())

    def value_in_time(self, time):
        m = max(x for x in self.setting.keys() if x <= time)
        return self.setting[m]


class SellerBase:
    def __init__(self,):
        self.game_len = Game.the_row().length
        self.seller_name = "base"

    @staticmethod
    def get_items_to_price(price, items):
        """
        !!!TODO!!! Returns list of pairs (entity, amount) such that amounts are positive,
        and sum(entity.price * amount) is approximately price (but not higher)
        """
        if not items:
            return []
        items = list(items)
        chosen = items[0]
        return [(chosen, int(price / chosen.price))]

    def generate_one(self, time):
        raise NotImplemented()

    @staticmethod
    def estimate_price(auction, coef):
        """ Returns expected price of var_entity in comparison to items sold and bought.
        coef: coefficient of auction initial price with respect to the "real" value of buying/selling stuff
        """
        diff = sum(item.entity.price * item.amount for item in auction.auctioneditem_set.all())
        diff /= auction.var_entity.price
        """
        Example: coef = 0.1
        When buying, start at 0.1 price than expected.
        When offering, offer 10 times more than expected.
        """
        return diff * coef if diff >= 0 else diff / coef

    @staticmethod
    def add_auction_item(auction, entity, amount, visible=True, will_sell=True):
        return auction.auctioneditem_set.create(
            entity=entity,
            amount=amount,
            visible=visible,
            will_sell=will_sell
        )

    def generate(self):
        raise NotImplemented()


class RandomSellerBase(SellerBase):
    # abstract methods
    def max_buy_count(self, time):
        raise NotImplemented()

    def max_sell_count(self, time):
        raise NotImplemented()

    def max_buy_price(self, time):
        raise NotImplemented()

    def max_sell_price(self, time):
        raise NotImplemented()

    def income_coef(self, time):
        raise NotImplemented()

    def buying_entities(self, time):
        raise NotImplemented()

    def selling_entities(self, time):
        raise NotImplemented()

    def generate_one(self, time):
        sell = set(self.selling_entities(time))
        buy = set(self.buying_entities(time))

        var_ent = choice(list(sell | buy)) # Oh, set does not support indexing...
        if var_ent in sell:
            sell.remove(var_ent)
        if var_ent in buy:
            buy.remove(var_ent)

        auction = BlackAuction.objects.create(var_entity=var_ent, var_min=0)

        sell_set = rand_subset(sell, self.max_sell_count(time))
        sell_amounts = self.get_items_to_price(self.max_sell_price(time), sell_set)
        for x, c in sell_amounts:
            if c == 0:
                sell_set.remove(x)
        buy_set = rand_subset(sell - sell_set, self.max_buy_count(time), min_size=0 if sell_set else 1)
        buy_amounts = self.get_items_to_price(self.max_buy_price(time), buy_set)

        for ent, am in buy_amounts:
            if am > 0:
                self.add_auction_item(auction, ent, -am)
        for ent, am in sell_amounts:
            if am > 0:
                self.add_auction_item(auction, ent, am)

        auction.var_min = self.estimate_price(auction, self.income_coef(time))
        auction.save()


class RandomStuffRiscantSeller(RandomSellerBase):
    def __init__(self):
        super().__init__()
        self.name = "Dr. Kámen"

        # risk
        self.risks = EvolvingSetting({0: 0})

        # average time between auctions in seconds
        self.spans = EvolvingSetting({0: 12})

        # věci, za které bude černý trh nakupovat
        # 1. hodinu jenom minable
        # 2. hodinu markatable
        # 3. hodinu: všechno
        self.buying_stuff = EvolvingSetting({
            0: list(ents().filter(lambda x: x.is_minable and x.price < 60)),
            
            1/3: list(ents().filter(lambda e: e.is_minable or e.is_markatable)),
            
            0.05: list(ents().filter(lambda x: x.is_minable)),
            0.1: list(ents().filter(lambda x: x.is_minable)),
            0.3: list(ents()),
        })

        self.buying_entities = lambda time: map(ent, self.buying_stuff.value_in_time(time))

        # věci, které se v tu dobu budou prodávat
        # 1. hodinu listy 
        self.selling_stuff = EvolvingSetting({
            0: list(ents()).filter(lambda e: e.is_markatable)),
            0.1: list(ents().filter(lambda e: e.is_markatable)),
            # k nákupu jsou i aukce
            0.9: all_goods
        })

        self.selling_entities = lambda time: map(ent, self.selling_stuff.value_in_time(time))

        self.max_buy_setting = EvolvingSetting({
            0: 100,
            0.1: 200,
            0.12: 10000,
            0.22: 10 ** 8
        })

        self.max_buy_price = self.max_buy_setting.value_in_time

        self.max_sell_setting = EvolvingSetting({
            0: 100,
            0.1: 200,
            0.12: 10000,
            0.22: 10 ** 8
        })

        self.max_sell_price = self.max_sell_setting.value_in_time

        self.income_coef_setting = EvolvingSetting({
            0: 1
        })

        self.income_coef = self.income_coef_setting.value_in_time

        # maximální počet druhů položek v aukci (když jich je moc, tak je to
        # nepřehledný)
        self.max_sell_count = EvolvingSetting({
            0: 1,
            0.3: 5,
            # neomezený počet: tohle bude brutální!
            0.6: len(all_goods)
        }).value_in_time

        self.max_buy_count = EvolvingSetting({
            0: 1,
            0.3: 5,
            0.6: len(all_goods)
        }).value_in_time

    def generate(self):
        for x in range(0,100,20):
            self.generate_one(x/100)

        return
        # TODO

        #seconds = 0
        #perc_time = 0
        #while perc_time < 1:
        #    span = self.spans.value_in_time(perc_time)
        #    seconds += span
        #    perc_time = seconds / self.game_len.seconds

        #    self.generate_one(perc_time)


class TrivialSeller(SellerBase):

    def max_buy_count(self, time):
        return 10

    def max_sell_count(self, time):
        return 10

    def max_sell_price(self, time):
        return 150

    def max_buy_price(self, time):
        return 150

    def income_coef(self, time):
        return 1

    def generate(self):
        self.generate_one(0.01)

    def buying_entities(self, time):
        return [ent("Ticho"), ent("Písek")]

    def selling_entities(self, time):
        return [ent("Křemen"), ent("Žula")]


class StaticAuction(SellerBase):
    def __init__(self, coef, *args, **kwargs):
        '''coef: coef from estimate_price'''
        self.estimate = not 'var_min' in kwargs.keys()
        if self.estimate:
            kwargs['var_min'] = 0
        if 'begin' in kwargs:
            if not isinstance(kwargs['begin'], datetime.timedelta):
                assert 0<= kwargs['begin'] <=1
                kwargs['begin'] = datetime.timedelta(seconds=self.game_len*kwargs['begin'])
        self.coef = coef
        self.b = BlackAuction.objects.create(*args, **kwargs)

    def __enter__(self):
        return self.b

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.estimate:
            self.b.var_min = self.estimate_price(self.b, self.coef)
            self.b.save()


def generate_blackmarket(force=False):
    if BlackAuction.objects.count() > 0:
        if force:
            BlackAuction.objects.all().delete()
        else:
            return "[SKIP] BlackAuction"

    sellers = [
        #TrivialSeller(buf),
        RandomStuffRiscantSeller(),
    ]

    for f in sellers:
        f.generate()

    with StaticAuction(coef=1,
			begin=datetime.timedelta(minutes=10),
			var_entity=e('Oheň')) as b:
        b.add_item(e('Žula'), 1)
        b.add_item(e('Křemen'), 1)
