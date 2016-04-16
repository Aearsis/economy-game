from random import *
from data.settings import *

seed(123)

def randfloat(a,b):
	assert a<=b
	return a + random()*(b-a)

# relativní obtížnosti získání jednotlivých levelů surovin
L1 = 10
L2 = 15
L3 = 50

minable_pricelist = [ (l1,L1) for l1 in minable_1 ] + [ (l2,L2) for l2 in minable_2 ] + [ (l3,L3) for l3 in minable_3 ]

market_pricelist = []
a = L1
b = 30*L2
gap = (b-a)//len(markatable)
for x,e in zip(range(a,b,gap),markatable):
	market_pricelist.append((e,x))

max_price = market_pricelist[-1][1]

tools_pricelist = [ (t,int(max_price*randfloat(5,20))) for t in tools ]

strategical_pricelist = [ (s,int(max_price*randfloat(0.8,4))) for s in strategical ]


# make dicts:
all_pricelist = dict(minable_pricelist+market_pricelist+tools_pricelist+strategical_pricelist)
minable_pricelist = dict(minable_pricelist)
market_pricelist = dict(market_pricelist)
tools_pricelist = dict(tools_pricelist)
strategical_pricelist = dict(strategical_pricelist)


# cena makable surovin je vždy (3-5)-krát vyšší než cena vstupních surovin
makable_pricelist = {}
queue = [ r for r in recipes ]
while queue:
	r = queue.pop(0)
	try:
		# TODO: after vaiable consumes number change also this
		needs_cost = sum(all_pricelist[n]*1 for n in r.consumes)
	except KeyError:
		queue.append(r)
		continue
	final_cost = (needs_cost*randint(3,5))//len(r.creates)
	for c in r.creates:
		makable_pricelist[c] = final_cost
		all_pricelist[c] = final_cost

if __name__ == "__main__":
	print(all_pricelist)
	print(len(all_pricelist.keys()))
	print(len(all_goods))
	print()
	print(makable_pricelist)
