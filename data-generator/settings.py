
########### Normální suroviny, na které není potřeba žádná licence. Jsou
########### mezi nimi jak ty, které se dají dostat sběrem, tak ty, s kterými
########### se obchoduje.
normal = """
Kly
Zuby žavlozubého tygra
Králičí žebra

Tygří kožešina
Mamutí kožešina
Králičí kožeina

Látky

Ebenové dřevo
Cedrové dřevo
Smrkové dřevo
""".split("\n")


#ILEGÁLNÍ SUROVINY
#-----------------
normal_ilegal = """
ticho
oheň
komiksy na kamených destičkách
semínka trávy
Venuše
""".split("\n")

#JÍDLO
#-----
normal += """
čistá voda
med
houbička
ovoce
bylinky
sušené maso 
""".split("\n")

#DEKORACE A JINÉ
#---------------
normal += """
bambusová rohožka
kulaté kamínky na cvrnkání
proutěná ošatka
kokosové misky
""".split("\n")

#KAMENY
#------
normal += """
lávové kameny
kamené chodníkové dlaždice
kamené cihly
mlýnský kámen
leštěné sluneční kamínky
zkamenělina trilobita
fosilie amonit
monolit
""".split("\n")

#DALŠÍ
#------
normal += [
	"hroší kůže",
	"dobrej pocit",
	]




########################################################
# licencované zboží

licenced = { # licence : [ list of licensed entities ]
	"Pazourková pila & Tesařský průkaz": [
		"Ebenová prkna",
		"Cedrová prkna",
		"Smrková prkna",
		],

	"Pazourková sekerka": [
		"Ebenová polínka",
		"Cedrová polínka",
		"Smrková polínka"
		],

	"Pazourkové nůžky": [
		"Kožená šňůrka",
		"Provázek",
		"Lepící kámen", # ~ izolepa, ale pšt!
		"Pazourek",
		],

	"Nástrojářský průkaz": """Pazourkové kladivo
Pazourková sekera
Pazourkové nůžky
Pazourková pila
Pazourkové dláto
Žula
Kamenec
Mastek
Křemen
Slída
Sádra
Vosk
pazourek
proutěné koště
pila z piraních zubů
dřevěná palice
kamená palice
brousek na odstraňování zubního kamene
Hliněné tabulky""".split("\n"),


# tohle by asi měli být recipes, že? klidně je časem můžeme vyhodit
# a před
	"Pazourkové dláto, Tesařský průkaz & Vosk": [
		"RandomSort",
		],

	"Pazourkové dláto, Tesařský průkaz & Mastek": [
		"InsertSort",
		],

	"Pazourkové dláto, Tesařský průkaz & Žula": [
		"BubbleSort",
		],

	"Pazourkové dláto, Tesařský průkaz & Křemen": [
		"QuickSort",
		],

	"Pazourkové kladivo, Pazourkové dláto, QuickSort, Křemen, Žula, Kamenec":[
		"Robot",
		]

}

normal = [ l.strip() for l in normal if l and not l.isspace() ]

if __name__ == "__main__":
	print("máme ve hře",len(normal),"nelicencovaných surovin:","\n".join(normal))
