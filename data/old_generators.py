
class BlackAuctionGenerator:
	'''This is an abstract class'''

	def __init__(self):
		self.game_len = Game.the_row().length

		self.buffer = []

	def create_auction_object(self,entity="Kel"):
		a = BlackAuction(
			begin=datetime.timedelta(seconds=1),
			end=None,
			var_entity=get_or_create_ent(entity),
			var_min = 10,
			seller_name=seller_name(),
			status_text=fair_status()
			)
		self.buffer.append(a)
		return a

	def set_random_time(self,auction,beg=None,end=None):
		'''beg a end jsou čísla mezi 0 a 1, podíl z uplynulého času hry, ve
		kterém se objeví aukce
		'''
		if beg is None:
			beg = 0
		if end is None:
			end = 1
		auction.begin = datetime.timedelta(seconds=int(randfloat(beg,end)*self.game_len.seconds))
		return auction

	def add_auc_item(self,auction,entity_name,amount=1,visible=True,will_sell=True):
		auction.save()
		item = AuctionedItem(
			auction=auction,
			entity=get_or_create_ent(entity_name),
			amount=amount,
			visible=visible,
			will_sell=will_sell
			)
		self.buffer.append(item)
		return item

	def generate(self):
		raise NotImplemented("override this in descendant class")
		
	def flush(self):
		for a in self.buffer:
			a.save()


class LicenceBAGenerator(BlackAuctionGenerator):
	'''asi 5 minut na začátku hry dá na prodej všechny licence, každou jednou za
	20-30 surovin z 2. levelu. To znamená, že všechny licence dá na prodej
	docela levně bez ohledu na ceník.'''

	def generate(self):
		for t in tools:
			a = self.create_raw_auction(choice(minable_2))
			a.var_min = choice(range(20,30))
			a.save()
			self.add_auc_item(a, t)
			self.set_random_time(a, 0.05, 0.05)


class EvolvingSetting:
	
	def __init__(self, setting):
		'''setting: list of pairs (percent_time, value) or a dict. In percent_time
		a setting will be changed to value
		'''

		self.setting = dict(setting)
		assert 0 in self.setting, 'setting must contain 0 (initial value)'
		assert all(0<= x <=1 for x in self.setting.keys())

	def value_in_time(self,time):
		m = max(x for x in self.setting.keys() if x<=time)
		return self.setting[m]


class RandomStuffRiscantBAGenerator(BlackAuctionGenerator):

	def __init__(self):
		super().__init__()

		
	def fair_or_fake(self,time,override_risk=None):
		'''False: fake, True: fair'''
		if override_risk:
			risk = override_risk
		else:
			risk = self.risks.value_in_time(time)
		if random()<risk:
			return False
		return True

	# TODO: tohle bude potřeba přepsat, zároveň to vrací zboží na prodej a na
	# nákup a je to hnus
	def random_goods_for_cost(self,cost,time,sell=True):
		if sell:
			setting = self.selling_stuff
			maxit = self.maxitems.value_in_time(time)
		else:
			setting = self.buying_stuff
			maxit = 1

		if cost>1000 and sell:
			step=1000
		else:
			step=1
#		print("všechny",setting.value_in_time(time))
		sell_menu = setting.value_in_time(time)
		if maxit < len(sell_menu):
			sell_menu = sample(sell_menu,maxit)
#		print("sample",sell_menu)
		actual_sell = []
		actual_price = 0
		i = True
		while actual_price<cost or i:
			i = False
			sell = choice(sell_menu)
			actual_price += step*all_pricelist[sell]
			actual_sell.extend([sell]*step)
		return actual_sell


	def create_fair_auction(self,time,buy_entity,amount_entity):
		a = BlackAuction(
			begin=datetime.timedelta(seconds=self.game_len.seconds*time),
			end=datetime.timedelta(minutes=10),
			var_entity_id=get_or_create_ent(buy_entity).id,
			var_min = amount_entity,
			seller_name=seller_name(),
			status_text=fair_status()
			)
		self.buffer.append(a)
		return a

	def create_fake_auction(self,time,buy_entity,amount_entity):
		a = BlackAuction(
			begin=datetime.timedelta(seconds=self.game_len.seconds*time),
			end=datetime.timedelta(minutes=10),
			var_entity_id=get_or_create_ent(buy_entity).id,
			var_min = amount_entity,
			seller_name=seller_name(),
			status_text=fake_status()
			)
		self.buffer.append(a)
		return a


	def create_random_stuff_auction(self, time):
		# cena zboží, které černý trh kupuje
		costlimit = randfloat(100,self.costlimit.value_in_time(time))

		buy = self.random_goods_for_cost(time, costlimit, sell=False)
		am = len(buy)
		buy = buy[0]

		will_sell = self.fair_or_fake(time)
		if will_sell:
			a = self.create_fair_auction(time,buy,am)
		else:
			a = self.create_fake_auction(time,buy,am)

		
		profit = self.profits.value_in_time(time)
		actually_sell = self.random_goods_for_cost(profit*costlimit,time)

		for i in set(actually_sell):
			c = actually_sell.count(i)
			if isinf(costlimit):
				c = randint(10,100)
			if will_sell:
				ws = True
			else:
				# u fakových transakcí hráč doopravdy dostane jenom 10% položek
				ws = self.fair_or_fake(time, override_risk=0.9)
			self.add_auc_item(a, i, amount=c,will_sell=ws)


	
	def generate(self):


		# pár vzorových aukcí se vygeneruje takhle
#		for x in range(0,100,5):
#			self.create_random_stuff_auction(x/100)

		seconds = 0
		perc_time = 0
		while perc_time < 1:
			span = self.spans.value_in_time(perc_time)
			seconds += span
			perc_time = seconds/self.game_len.seconds

			self.create_random_stuff_auction(perc_time)


