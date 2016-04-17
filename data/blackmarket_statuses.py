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
        "%(seller)s uzavrel obchod s týmem %(buyer)s o koupi %(advertised)s, ale příšlo místo toho %(bought)s!",
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
