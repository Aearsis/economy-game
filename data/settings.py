from collections import namedtuple

Recipe_tuple = namedtuple("Recipe_tuple", "consumes needs creates")

# rozdělení minable surovin podle obtížnosti (podle toho, jak daleko budou
# umístěny)
minable_1 = """Písek
Kamení
Mamutí kel
Žebírka
Smrk
Tygří kožešina
Mamutí kožešina
Králičí kožešina""".split("\n")

minable_2 = """Čistá voda
Medvědí česnek
Křemen
Zub šavlozubého tygra""".split("\n")

# level 3 může být ty suroviny na ostrůvku
minable_3 = """Med
Dobrej pocit""".split("\n")

minable = minable_1 + minable_2 + minable_3

# seřazené podle toho, jak ty suroviny budou na černém trhu drahé
markatable = """Sušené maso
Vosk
Mastek
Žula
Kamenec
Pazourek
Bambusová rohožka
Kulaté kamínky na cvrnkání
Proutěná ošatka
Kokosové misky
Kokosová miska
Lávové kameny
Kamenné dlaždice
Kamenné cihly
Mlýnský kámen
Mýdlo
Leštěné sluneční kamínky
Zkamenělina trilobita
Monolit
Ticho
Eben
Oheň
Kamenná destička s komiksem
Semínka trávy
Venuše
Burák""".split("\n")

makable = """Kožená šňůrka
Robot
RandomSort
BubbleSort
InsertSort
QuickSort
Cedr
Lepící kámen
Cedrové prkno
Smrkové prkno
Ebenové prkno
Cedrová deska
Smrková deska
Ebenová deska
Cedrové polínko
Ebenové polínko
Smrkové polínko
Špagát""".split("\n")

# licence k receptům
tools = """Pazourková sekera
Pazourkové nůžky
Pazourkové dláto
Pazourkové kladivo
Pazourková pila
Střihačské oprávnění
Tesařský průkaz
Nástrojářský průkaz""".split("\n")

all_goods = minable + makable + markatable + tools

strategical = """Ebenové prkno
Kožená šňůrka
Špagát
Lepící kámen
Mýdlo
Oheň
Robot
Lávové kameny
Žula
Pazourek
Křemen
Leštěné sluneční kamínky""".split("\n")


# OH: Spadlo by to samo na ent(x)
def check_strategical():
    for e in strategical:
        assert e in all_goods, e + " is a strategical entity, but it must be mentioned first above"


# list of pairs (license, licenced entity)
# both must be mentioned among all_goods before
licences = [
               ("Nástrojářský průkaz", i) for i in """Pazourkové dláto
Pazourkové kladivo
Pazourková pila
Tesařský průkaz""".split("\n")
               ] + [
               ("Střihačské oprávnění", "Pazourkové nůžky")
           ]


# OH: Spadlo by to samo na ent(x)
def check_licences():
    for a, b in licences:
        assert a in all_goods, "%s unknown, although it's a licence. It must be mentioned earlier." % a
        assert b in all_goods, "%s unknown although it's a licenced entity. It must be mentioned earlier." % b


# TODO: it doesn't allow numbers of consume or create now
recipes = [
              Recipe_tuple(
                  needs=("Pazourková pila", "Tesařský průkaz"),
                  consumes={tree: 1},
                  creates={tree + "ové prkno": 3},
              )
              for tree in ["Cedr", "Smrk", "Eben"]
              ] + [
              Recipe_tuple(
                  needs=("Pazourková sekera",),
                  consumes={tree: 1},
                  creates={tree + "ové polínko": 3},
              )
              for tree in ["Cedr", "Smrk", "Eben"]
              ] + [
              Recipe_tuple(
                  needs=("Pazourkové nůžky",),
                  consumes={kuze: 1},
                  creates={provazek: 10},
              )
              for kuze in ["Tygří kožešina", "Mamutí kožešina", "Králičí kožešina"]
              for provazek in ["Kožená šňůrka", "Špagát"]
              ] + [
              Recipe_tuple(
                  needs=("Pazourkové nůžky",),
                  consumes={"Mamutí kožešina": 1},
                  creates={provazek: 100},
              )
              for provazek in ["Kožená šňůrka", "Špagát"]
              ] + [
              Recipe_tuple(
                  needs=(),
                  consumes={"Med": 1, "Čistá voda": 1, "Kamení": 1},
                  creates={"Lepící kámen": 1},
              ),

              Recipe_tuple(
                  needs=("Pazourkové dláto", "Tesařský průkaz"),
                  consumes={"Vosk": 1},
                  creates={"RandomSort": 1},
              ),

              Recipe_tuple(
                  needs=("Pazourkové dláto", "Tesařský průkaz"),
                  consumes={"Mastek": 1},
                  creates={"InsertSort": 1},
              ),

              Recipe_tuple(
                  needs=("Pazourkové dláto", "Tesařský průkaz"),
                  consumes={"Mýdlo": 1, "Čistá voda": 1},
                  creates={"BubbleSort": 1},
              ),

              Recipe_tuple(
                  needs=("Pazourkové dláto", "Tesařský průkaz"),
                  consumes={"Křemen": 1},
                  creates={"QuickSort": 1},
              ),

              Recipe_tuple(
                  needs=("Pazourkové kladivo", "Pazourkové dláto"),
                  consumes={"QuickSort": 1, "Křemen": 1, "Žula": 1, "Kamenec": 1, "Dobrej pocit": 1},
                  creates={"Robot": 1},
              ),
          ]


# check recipes: všechny ingredience a výrobky musí být zmíněné dříve mezi
# minable, markatable etc., aby se nestalo, že nějaká věc je nedostupná!!!

# TODO: asi by bylo fajn stanovit u receptů taky množství, ale do toho se mi
# moc nechce. Všechno bude jenom jednou (nebo náhodné číslo z 1-3)-krát.
# OH: Uvedení víckrát bude fungovat.

# print(recipes)

# OH: Spadlo by to samo na ent(x)


def check_recipes():
    for r in recipes:
        assert all(n in tools for n in r.needs), "Recipe_tuple needs undefined " + str(r)
        for c in r.consumes:
            assert c in all_goods, str(c) + " unknown"
        for c in r.creates:
            assert c in all_goods, str(c) + " unknown " + str(r)


def check():
    check_strategical()
    check_licences()
    check_recipes()
    print("check OK")


# comment to disable it
check()

if __name__ == "__main__":
    print("všech surovin", len(all_goods))
    print("minable", len(minable))
    print("markatable", len(markatable))
    print("strategical", len(strategical))
    print("makable", len(makable))
