from random import choice
from data import generated


def fair_status():
    # Používejte následující náhrady:
    #  %(seller)s - jméno prodávajícího (Franta Vomáčka)
    #  %(buyer)s - kupující tým (Kamenolom)
    #  %(bought)s - koupeno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)
    #  %(sold)d - prodáno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)
    return choice([
        "Tým %(buyer)s koupil od %(seller)s %(bought)s za %(sold)s.",
        "Tým %(seller)s málem nedodal %(bought)s pro %(buyer)s, ale nakonec vše dorazilo v pořádku.",
        # ...
    ])


def fake_status():
    # Používejte náhrady jako výše, navíc:
    #  %(advertised)s - původně nabízeno (1ks Izolepa, 1ks Kámen a 3m Dobrej pocit)

    return choice([
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
