from collections import namedtuple
Recipe = namedtuple("Recipe", "consumes needs creates")

minable = """Kly
Zuby žavlozubého tygra
Králičí žebra
Tygří kožešina
Mamutí kožešina
Králičí kožešina
Eben
Cedr
Smrk
Čistá voda
Med
Medvědí česnek
Dobrej pocit
Písek
Kamení
Křemen
""".split("\n")

blackmarkatable = """Ticho
Oheň
Komiksy na kamených destičkách
Semínka trávy
Venuše
Burák
""".split("\n")

makable_markatable = """
sušené maso 
Vosk
Mastek
Žula
Kamenec
bambusová rohožka
kulaté kamínky na cvrnkání
proutěná ošatka
kokosové misky
lávové kameny
kamené chodníkové dlaždice
kamené cihly
mlýnský kámen
Mýdlo
Cedrové prkno
Ebenové prkno
Smrkové prkno
Cedrové polínko
Ebenové polínko
Smrkové polínko
leštěné sluneční kamínky
Lepící kámen
zkamenělina trilobita
monolit
Robot
RandomSort
BubbleSort
InsertSort
QuickSort
Kožená šňůrka
Provázek
""".split("\n")


all_goods = minable + blackmarkatable + makable_markatable


tools = """Pazourková sekerka
Pazourkové nůžky
Pazourkové dláto
Pazourkové kladivo
Pazourková pila
Tesařský průkaz
Nástrojářský průkaz""".split("\n")

recipes = [
	Recipe(
		needs=("Pazourková pila","Tesařský průkaz"),
		consumes=(tree,),
		creates=(tree+"ové prkno",)
	) for tree in ["Cedr","Smrk","Eben"]
	] + [

	Recipe(
		needs=("Pazourková sekerka",),
		consumes=(tree,),
		creates=(tree+"ové polínko",)
	) for tree in ["Cedr","Smrk","Eben"]
	] + [
	Recipe(
		needs=(),
		consumes=("Med","Čistá voda","Kamení"),
		creates=("Lepící kámen",),
		)
	] + [
	Recipe(
		needs=("Pazourkové nůžky",),
		consumes=(kuze,),
		creates=(provazek,)
	) for kuze in ["Tygří kožešina","Mamutí kožešina","Králičí kožešina"] \
	for provazek in ["Kožená šňůrka","Provázek"]
	] + [

	Recipe(
		needs=("Pazourkové dláto","Tesařský průkaz"),
		consumes=("Vosk",),
		creates=("RandomSort",)
		),

	Recipe(
		needs=("Pazourkové dláto", "Tesařský průkaz"),
		consumes=("Mastek",),
		creates=("InsertSort",)
	),

	Recipe(
		needs=("Pazourkové dláto", "Tesařský průkaz"),
		consumes=("Mýdlo","Čistá voda"),
		creates=("BubbleSort",)
	),

	Recipe(
		needs=("Pazourkové dláto","Tesařský průkaz"),
		consumes=("Křemen",),
		creates=("QuickSort",)
		),

	Recipe(
		needs=("Pazourkové kladivo", "Pazourkové dláto"),
		consumes=("QuickSort", "Křemen", "Žula", "Kamenec"),
		creates=("Robot",)
		),
]

# check recipes: všechny ingredience a výrobky musí být zmíněné dříve mezi
# minable, markatable etc., aby se nestalo, že nějaká věc je nedostupná!!!

# TODO: asi by bylo fajn stanovit u receptů taky množství, ale do toho se mi
# moc nechce. Nechal bych všechno jednou.

for r in recipes:
	assert all(n in tools for n in r.needs), "Recipe needs undefined "+str(r)
	for c in r.consumes:
		assert c in all_goods, str(c)+" unknown"
	for c in r.creates:
		assert c in all_goods, str(c)+" unknown "+str(r)
		 
