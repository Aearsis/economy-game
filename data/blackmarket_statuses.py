from random import choice
from data import generated


def fair_status():
    # Používejte následující náhrady:
    #  %(seller)s - jméno prodávajícího (Franta Vomáčka)
    #  %(buyer)s - kupující tým (Kamenolom)
    #  %(bought)s - koupeno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)
    #  %(sold)s - prodáno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)
    return choice([
        "Tým %(buyer)s koupil od %(seller)s %(bought)s za %(sold)s.",
        "Tým %(seller)s málem nedodal %(bought)s pro %(buyer)s, ale nakonec vše dorazilo v pořádku.",
        "%(seller)s právě výhodně prodal %(sold)s."
        "%(buyer)s právě výhodně koupil %(bought)s."
        "Úspěšně proběhla výměna %(bought)s a %(sold)s mezi %(buyer)s a %(seller)s."
        "Tým %(buyer)s právě nakoupil %(bought)s. No... kdo chce kam, pomožme mu tam."
        "Za zvýhodněnou cenu %(sold)s právě %(buyer)s nakoupil %(bought)s od %(seller)s."
        "Tým %(buyer)s právě nakoupil %(bought)s. Otázkou je, k čemu jim to bude?"
        "Tým %(buyer)s právě nakoupil %(bought)si. Stojí za úvahu, zda to bylo dobře."
        "Právě bylo prodáno %(sold)s za %(bought)s."
        "%(buyer)s zakoupil %(bought)s za %(sold)s."
        "Už je prodáno %(sold)s za cenu %(bought)s."
        "Poprvé, podruhé, potřetí. Prodáno %(sold)s týmu %(buyer)s za %(bought)s."
        "Týmu %(buyer)s bylo přiklepnuto %(bought)s za %(sold)s."
        "Hroší bozi požehnali a urodilo se %(bought)s, což bylo v zápětí prodáno týmu %(buyer)s."
        "Nejvyšší hroch svolil k výměně mezi %(seller)s a %(buyer)s."
        "Piraní dopravní služba právě dovezla %(bought)s k %(buyer)s."
        "Mamutí nákladní expres právě fofrem dovezl %(bought)s k %(buyer)s."
        "Týmu %(buyer)s šavlozubí holubi doručili zásilku %(bought)s."
        "Zásilka %(sold)s byla přepadena kamenožrouty a zničena. %(buyer)s obdžel %(bought)s, avšak odmítl nahradit škodu."
        "Byl uzavřen obchod mezi %(seller)s a %(buyer)s."
        "%(seller)s prodal %(sold)s."
        "%(buyer)s koupil %(bought)s."
        "Za %(bought)s bylo zakoupeno %(sold)s."
        "Tým %(buyer)s si objednal %(bought)s."
        "Tým %(buyer)s zaplatil vysokou cenu %(sold)s, vyšlo ho to fakt draze."
        "Právě proběhl pokus o krádež %(bought)s, ale %(buyer)s byl načapán a musel zaplatit %(sold)s."
        "Přesně %(sold)s stálo %(buyer)s koupit %(bought)s."
        "Tak tak se stihl %(seller)s zbavit %(sold)s před datem expirace."
        "%(buyer)s právě prohloupil nákupem %(bought)s, už ale svoje %(sold)s nikdy neuvidí."
        "%(buyer)s výhodně získal %(bought)s."
        "Vyměnili byste %(sold)s za %(bought)s? Tým %(buyer)s to právě udělal."
        "%(seller)s ví, jak se rychle zbavit %(sold)s."
        "%(buyer)s vyhodil právě %(sold)s z okna, literárně řečeno."
        "%(seller)s se zrovna zbavil %(sold)s."
        # ...
    ])


def fake_status():
    # Používejte náhrady jako výše, navíc:
    #  %(advertised)s - původně nabízeno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)

    return choice([
        "Být či nebýt... to není správná otázka. Koupit či nekoupit, to je oč tu běží."
        "%(seller)s uzavřel obchod s týmem %(buyer)s o koupi %(advertised)s, ale příšlo místo toho %(bought)s!",
        "%(seller)s pěkně vypekl tým %(buyer)s, místo %(advertised)s poslal %(bought)s!",
        "Víte jaké to je, když chcete koupit %(advertised)s, ale místo toho %(bought)s přijde? No, %(buyer)s už to ví!",
        "%(seller)s přišel o %(advertised)s, sežrali mu to kamenožrouti, ale aspoň poslal %(bought)s.",
        "%(buyer)s má prostě smůlu, ale lepší %(bought)s v hrsti než-li %(advertised)s na střeše.",
        "%(buyer)s zaplatili za %(advertised)s, ale příšlo jenom %(bought)s.",
        "Tým %(buyer)s koupil %(advertised)s, eeh, vlastně teda %(bought)s.",
        "%(seller)s okradl tým %(buyer)s o %(sold)s, pojišťovna zaplatila pouze %(bought)s.",
        "Oslavujte Hroší bohy! Stal se zázrak %(seller)s poslal %(advertised)s, ale k %(buyer)s dorazilo %(bought)s.",
        "%(seller)s se omlouvá týmu %(buyer)s...",
        # ...
    ])


def seller_name():
    return choice([
                      "Mr. Stone",
                      "Dr. Kámen",
                      "anonymní obchodník",
                  ] * 10
                  + generated.names_cs()
                  )
