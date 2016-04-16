from random import *
from data.settings import *


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
max_price = 30*L2
gap = (max_price-a)//len(markatable)
for e,x in zip(markatable,range(a,max_price,gap)):
	market_pricelist.append((e,x))


tools_pricelist = [ (t,int(max_price*randfloat(5,20))) for t in tools ]

strategical_pricelist = [ (s,int(max_price*randfloat(0.8,4))) for s in strategical ]


# make dicts:
all_pricelist = dict(minable_pricelist + market_pricelist + tools_pricelist)

# override prices of strategical entites
for k,v in strategical_pricelist:
	all_pricelist[k] = v

# cena makable surovin je vždy (3-5)-krát vyšší než cena vstupních surovin
queue = [ r for r in recipes ]
# if this creates an infinite loop then there is a cycle between makable entities
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
		all_pricelist[c] = final_cost


for e in makable:
	if not e in all_pricelist:
		print("WARNING: there exists a makable entity %s, but any receipt creates it!!!" % e)
		all_pricelist[e] = 0

print(all_pricelist)
if __name__ == "__main__":
	print(len(all_pricelist.keys()))
	print(len(all_goods))
	print()
