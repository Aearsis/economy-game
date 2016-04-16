from collections import namedtuple

r = namedtuple("recipe_tuple", "consumes needs creates creates_num")
class Recipe_tuple(r):

	def __new__(self,consumes,needs,creates,creates_num=None):
		return super().__new__(self,consumes,needs,creates,creates_num)

#	def __new__(self,consumes,needs,creates,creates_num=None):

minable = """Kel
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
Křemen""".split("\n")

blackmarkatable = """Ticho
Oheň
Komiksy na kamených destičkách
Semínka trávy
Venuše
Burák""".split("\n")

markatable = """sušené maso 
Vosk
Mastek
Žula
Kamenec
Pazourek
Bambusová rohožka
Kulaté kamínky na cvrnkání
Proutěná ošatka
Kokosové misky
Lávové kameny
Kamené chodníkové dlaždice
Kamené cihly
Mlýnský kámen
Mýdlo
Leštěné sluneční kamínky
Zkamenělina trilobita
Monolit""".split("\n")

makable = """Kožená šňůrka
Robot
RandomSort
BubbleSort
InsertSort
QuickSort
Lepící kámen
Cedrové prkno
Smrkové prkno
Ebenové prkno
Cedrové polínko
Ebenové polínko
Smrkové polínko
Provázek""".split("\n")

all_goods = minable + blackmarkatable + makable + markatable

strategical = """Ebenové prkno
Kožená šňůrka
Provázek
Lepící kámen
Mýdlo
Oheň
Robot
Lávové kameny
Žula
Pazourek
Křemen
Leštěné sluneční kamínky""".split("\n")


for e in strategical:
	assert e in all_goods, e+" is unknown"

tools = """Pazourková sekerka
Pazourkové nůžky
Pazourkové dláto
Pazourkové kladivo
Pazourková pila
Tesařský průkaz
Nástrojářský průkaz""".split("\n")

licences = {
	("Nástrojářský průkaz",):"""Pazourková sekerka
Pazourkové dláto
Pazourkové kladivo
Pazourková pila
Tesařský průkaz""".split("\n"),

	("Stříhačské oprávnění",):["Pazourkové nůžky"],
	
}

recipes = [
	Recipe_tuple(
		needs=("Pazourková pila","Tesařský průkaz"),
		consumes=(tree,),
		creates=(tree+"ové prkno",)
	) for tree in ["Cedr","Smrk","Eben"]
	] + [

	Recipe_tuple(
		needs=("Pazourková sekerka",),
		consumes=(tree,),
		creates=(tree+"ové polínko",)
	) for tree in ["Cedr","Smrk","Eben"]
	] + [
	Recipe_tuple(
		needs=(),
		consumes=("Med","Čistá voda","Kamení"),
		creates=("Lepící kámen",),
		)
	] + [
	Recipe_tuple(
		needs=("Pazourkové nůžky",),
		consumes=(kuze,),
		creates=(provazek,)
	) for kuze in ["Tygří kožešina","Mamutí kožešina","Králičí kožešina"] \
	for provazek in ["Kožená šňůrka","Provázek"]
	] + [

	Recipe_tuple(
		needs=("Pazourkové nůžky",),
		consumes=("Mamutí kožešina",),
		creates=(provazek,),
		creates_num=(100,)
	) for provazek in ["Kožená šňůrka","Provázek"]

	] + [


	Recipe_tuple(
		needs=("Pazourkové dláto","Tesařský průkaz"),
		consumes=("Vosk",),
		creates=("RandomSort",)
		),

	Recipe_tuple(
		needs=("Pazourkové dláto", "Tesařský průkaz"),
		consumes=("Mastek",),
		creates=("InsertSort",)
	),

	Recipe_tuple(
		needs=("Pazourkové dláto", "Tesařský průkaz"),
		consumes=("Mýdlo","Čistá voda"),
		creates=("BubbleSort",)
	),

	Recipe_tuple(
		needs=("Pazourkové dláto","Tesařský průkaz"),
		consumes=("Křemen",),
		creates=("QuickSort",)
		),

	Recipe_tuple(
		needs=("Pazourkové kladivo", "Pazourkové dláto"),
		consumes=("QuickSort", "Křemen", "Žula", "Kamenec"),
		creates=("Robot",)
		),
]

# check recipes: všechny ingredience a výrobky musí být zmíněné dříve mezi
# minable, markatable etc., aby se nestalo, že nějaká věc je nedostupná!!!

# TODO: asi by bylo fajn stanovit u receptů taky množství, ale do toho se mi
# moc nechce. Nechal bych všechno jednou.

print(recipes)

for r in recipes:
	assert all(n in tools for n in r.needs), "Recipe_tuple needs undefined "+str(r)
	for c in r.consumes:
		assert c in all_goods, str(c)+" unknown"
	for c in r.creates:
		assert c in all_goods, str(c)+" unknown "+str(r)
		 
