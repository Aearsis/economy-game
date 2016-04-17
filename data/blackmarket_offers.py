
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
    return set(superset)

    size = randint(min_size, max_size)

    if size >= len(superset):
        return set(superset)

    shuffle(superset)
    return set(superset[:size])


def ent_filter(**kwargs):
    return Entity.objects.filter(**kwargs).all()

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

        auction = BlackAuction.objects.create(var_min=0)

        sell_set = rand_subset(sell, self.max_sell_count(time))
        sell_amounts = self.get_items_to_price(self.max_sell_price(time), sell_set)
        for x, c in sell_amounts:
            if c == 0:
                sell_set.remove(x)

        buy_set = rand_subset(sell - sell_set, self.max_buy_count(time), min_size=0 if sell_set else 1)
        buy_amounts = self.get_items_to_price(self.max_buy_price(time), buy_set)
        for x, c in buy_amounts:
            if c == 0:
                buy_set.remove(x)

        price = 0
        for ent, am in buy_amounts:
            if am > 0:
                self.add_auction_item(auction, ent, -am)
                price += am * ent.price

        for ent, am in sell_amounts:
            if am > 0:
                self.add_auction_item(auction, ent, am)
                price += am * ent.price

        auction.var_entity = choice(list(sell_set if price > 0 else buy_set))
        auction.var_min = self.estimate_price(auction, self.income_coef(time))
        auction.save()


class RandomStuffRiscantSeller(RandomSellerBase):
    def __init__(self):
        super().__init__()
        self.name = "Dr. Kámen"

        # risk
        self.risks = EvolvingSetting({0: 0, 0.15: 0.1, 0.5: 0.9, 0.52: 0.15})

        # average time between auctions in seconds
        self.spans = EvolvingSetting({0: 12})

        # věci, za které bude černý trh nakupovat
        # 1. hodinu jenom minable
        # 2. hodinu markatable
        # 3. hodinu: všechno
        self.buying_entities = EvolvingSetting({
            0: ent_filter(is_minable=True),
            1 / 3: Entity.objects.exclude(is_minable=False, is_markatable=False).all(),
            2 / 3: Entity.objects.all(),
        }).value_in_time

        # věci, které se v tu dobu budou prodávat
        self.selling_entities = EvolvingSetting({
            0: ent_filter(is_markatable=True),
            1/3: Entity.objects.exclude(is_minable=False, is_markatable=False).all(),
        }).value_in_time

        self.max_buy_price = EvolvingSetting({
            0: 0,
            1/6: 60,
            1/3: 600,
            2/3: 2**32,
        }).value_in_time

        self.max_sell_setting = EvolvingSetting({
            0: 60,
            1/6: 120,
            1/3: 600,
            1/2: 2**32,
        })

        self.max_sell_price = self.max_sell_setting.value_in_time

        self.income_coef = EvolvingSetting({
            0: 30,
            1/12: 20,
            1/6: 10,
            1/3: 5,
            1/2: 2
        }).value_in_time

        # maximální počet druhů položek v aukci (když jich je moc, tak je to
        # nepřehledný)
        self.max_sell_count = EvolvingSetting({
            0: 2,
            1/3: 5,
            5/6: 10
        }).value_in_time

        self.max_buy_count = EvolvingSetting({
            0: 0,
            1 / 6: 1,
            1 / 3: 3,
            2 / 3: 5,
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
        super().__init__()
        self.estimate = not 'var_min' in kwargs.keys()
        if self.estimate:
            kwargs['var_min'] = 0
        if 'begin' in kwargs:
            if not isinstance(kwargs['begin'], datetime.timedelta):
                assert 0<= kwargs['begin'] <=1
                kwargs['begin'] = datetime.timedelta(seconds=self.game_len.seconds*kwargs['begin'])
        if 'status_text' not in kwargs:
            kwargs['status_text'] = fair_status()
        self.coef = coef
        self.b = BlackAuction.objects.create(*args, **kwargs)

    def __enter__(self):
        return self.b

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.estimate:
            self.b.var_min = self.estimate_price(self.b, self.coef)
            self.b.save()
            
def e(name):
    return Entity.objects.get(name=name)

def sell_rafts_for_robots():
    def create(time):
        with StaticAuction(coef=1,
                        begin=time,
                        var_entity=choice(ent_filter(is_minable=True)),
                        seller_name="Igor Voloďa") as b:
            b.add_item(e('Robot'), 1)
            b.add_item(e('Vor'), -1)
    
    for _ in range(3): create(0)  # třikrát se objeví na začátku
    c = 60  # number of auctions
    for i in range(c):
        create(i/c)
        
def peanut_merchant():
    def create(time):
        b = BlackAuction(begin=time,end=None,
                          var_entity=e("Burák"),
                          var_min=1,
                          seller_name='Mgr. Burák')
        
        b.save()
        b.add_item(e('Robot'), -1)
    
    num = 10
    for i in range(num):
        create(1/3+i*1/15)
       

def generate_blackmarket(force=False):

    
    if BlackAuction.objects.count() > 0:
        if force:
            BlackAuction.objects.all().delete()
        else:
            return "[SKIP] BlackAuction"

    sell_rafts_for_robots()
    
    sellers = [
        #TrivialSeller(buf),
        RandomStuffRiscantSeller(),
    ]

    for f in sellers:
        f.generate()

 