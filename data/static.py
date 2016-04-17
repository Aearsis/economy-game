class EntityTuple:
    def __init__(self, name, price, token_amount=0, sell=None, strategic=False):
        self.name = name
        self.price = price
        self.token_amount = token_amount
        self.sell = sell if sell is not None else token_amount == 0
        self.strategic = strategic


all_goods = (
    EntityTuple("Smrk", 2, token_amount=30),
    EntityTuple("Voda", 2, token_amount=30),
    EntityTuple("Trilobit", 15, token_amount=4),
    EntityTuple("Cedrologický poradce", 600),
    EntityTuple("Marek Eben", 600),
    EntityTuple("Bambus", 60, token_amount=1),
    EntityTuple("Bambusová trubka", 60),
    EntityTuple("Blesky a hromy", 20),
    EntityTuple("Bubble sort", 1),
    EntityTuple("Burák", 1, sell=False),
    EntityTuple("Cedr", 60),
    EntityTuple("Cedrová deska", 300),
    EntityTuple("Cedrové prkno", 30, sell=False),
    EntityTuple("Cedrové polínko", 30, sell=False),
    EntityTuple("Dobrej pocit", 240, token_amount=1),
    EntityTuple("Dřevěná palice", 60),
    EntityTuple("Eben", 200),
    EntityTuple("Ebenová deska", 600),
    EntityTuple("Ebenové prkno", 60, sell=False),
    EntityTuple("Ebenové polínko", 60),
    EntityTuple("Fosilie amonit", 1),
    EntityTuple("Kamenná palice", 180),
    EntityTuple("Kamenná cihla", 1),
    EntityTuple("Kamenná destička s komiksy", 600),
    EntityTuple("Kamenná sekera", 360),
    EntityTuple("Kamenná dlaždice", 2),
    EntityTuple("Kamenné dláto", 600),
    EntityTuple("Kamenný lis", 600, sell=False),
    EntityTuple("Kladivo", 160),
    EntityTuple("Kožená šňůrka", 60),
    EntityTuple("Králičí kůže", 60, token_amount=1),
    EntityTuple("Krásnej šutr", 240, token_amount=1),
    EntityTuple("Kulaté kamínky na cvrnkání", 2),
    EntityTuple("Křemen", 1),
    EntityTuple("Lepicí kámen", 600),
    EntityTuple("Mamutí kůže", 60),
    EntityTuple("Med", 1),
    EntityTuple("Monolit", 1),
    EntityTuple("Mýdlo", 6),
    EntityTuple("Pazourek", 30),
    EntityTuple("Pazourková sekera", 200),
    EntityTuple("Pazourková pila", 200),
    EntityTuple("Pazourkové nůžky", 600),
    EntityTuple("Pazourkový nůž", 30),
    EntityTuple("Pila z piraních zubů", 300),
    EntityTuple("Plátky bambusu", 50),
    EntityTuple("Proutěná ošatka", 10),
    EntityTuple("Písek", 1),
    EntityTuple("Přízeň hroších bohů", 360),
    EntityTuple("Quick sort", 60),
    EntityTuple("Radix sort", 180),
    EntityTuple("Random sort", 5),
    EntityTuple("Rekurze", 2),
    EntityTuple("Robot", 600),
    EntityTuple("Smrková deska", 120),
    EntityTuple("Smrkové polínko", 5, sell=False),
    EntityTuple("Smrkové prkno", 5, sell=False),
    EntityTuple("Trilobajt", 240, sell=False),
    EntityTuple("Tygří kůže", 60),
    EntityTuple("Venuše", 30),
    EntityTuple("Vor", 600),
    EntityTuple("Včelí plástev", 120, token_amount=1),
    EntityTuple("Zub šavlozubého tygra", 6),
    EntityTuple("Špagát", 600),
    EntityTuple("Žebírka", 60),
    EntityTuple("Žula", 60, token_amount=1),
)

licences = (
    ("Cedrologický poradce", "Cedrová deska"),
    ("Marek Eben", "Ebenová deska"),
    ("Rekurze", "Rekurze"),
)


class RecipeTuple:
    def __init__(self, consumes={}, needs=(), creates={}, name=None, desc=None):
        self.consumes = consumes
        self.needs = needs
        self.creates = creates
        self.name = name
        self.desc = desc


recipes = [
    RecipeTuple(
        consumes={"Eben": 1},
        needs=("Kamenná sekyra"),
        creates={"Ebenové polínko": 5}
    ),
    RecipeTuple(
        consumes={"Ebenové polínko": 1, "Ebenové prkno": 1, "Zub šavlozubého tygra": 1, "Cedrová deska": 1},
        creates={"Ebenová deska": 1}
    ),
    RecipeTuple(
        consumes={"Eben": 1},
        needs=("Pila z piraních zubů"),
        creates={"Ebenové prkno": 6}
    ),
    RecipeTuple(
        consumes={"Zub šavlozubého tygra": 1, "Smrková deska": 1, "Cedrové polínko": 1, "Cedrové prkno": 1},
        creates={"Cedrová deska": 1}
    ),
    RecipeTuple(
        consumes={"Zub šavlozubého tygra": 1, "Smrkové polínko": 6, "Smrkové prkno": 6},
        creates={"Smrková deska": 1}
    ),
    RecipeTuple(
        consumes={"Smrk": 10},
        creates={"Smrkové polínko": 5}
    ),
    RecipeTuple(
        consumes={"Smrk": 10},
        creates={"Smrkové prkno": 5}
    ),
    RecipeTuple(
        consumes={"Cedr": 1},
        needs=("Pazourková sekera"),
        creates={"Cedrové polínko": 4}
    ),
    RecipeTuple(
        consumes={"Cedr": 1},
        needs=("Pazourková pila"),
        creates={"Cedrové prkno": 1},
    ),
    RecipeTuple(
        consumes={"Kožená šňůrka": 10, "Žebírka": 1},
        creates={"Špagát": 1},
    ),
    RecipeTuple(
        consumes={"Králičí kůže": 1},
        needs=("Pazourkové nůžky"),
        creates={"Kožená šňůrka": 1},
    ),
    RecipeTuple(
        consumes={"Tygří kůže": 1},
        needs=("Pazourkové nůžky"),
        creates={"Kožená šňůrka": 2},
    ),
    RecipeTuple(
        consumes={"Mamutí kůže": 1},
        needs=("Pazourkové nůžky"),
        creates={"Kožená šňůrka": 4},
    ),
    RecipeTuple(
        consumes={"Plátky bambusu": 10},
        needs=("Kamenný lis"),
        creates={"Bambusová trubka": 1},
    ),
    RecipeTuple(
        consumes={"Kamenná dlaždice": 150, "Kamenná cihla": 300},
        creates={"Kamenný lis": 600},
    ),
    RecipeTuple(
        consumes={"Pazourkový nůž": 4},
        creates={"Pazourková pila": 1},
    ),
    RecipeTuple(
        consumes={"Bambus": 2},
        needs=("Pazourkový nůž"),
        creates={"Plátky bambusu": 1},
    ),
    RecipeTuple(
        consumes={"Pazourek": 1},
        needs=("Kamenná palice"),
        creates={"Pazourkový nůž": 2},
    ),
    RecipeTuple(
        consumes={"Fosilie amonit": 60, "Blesky a hromy": 3},
        needs=("Přízeň hroších bohů"),
        creates={"Krásnej šutr": 1},
    ),
    RecipeTuple(
        consumes={"Krásnej šutr": 1, "Venuše": 4},
        needs=("Kamenná palice", "Kamenné dláto"),
        creates={"Kamenná destička s komiksy": 1},
    ),
    RecipeTuple(
        consumes={"Pazourek": 2, "Krásnej šutr": 1, "Písek": 60},
        creates={"Pazourkové nůžky": 1},
    ),
    RecipeTuple(
        consumes={"Písek": 20, "Med": 1},
        creates={"Burák": 1, "Křemen": 20}
    ),
    RecipeTuple(
        consumes={"Křemen": 20, "Voda": 1},
        creates={"Burák": 1, "Písek": 20}
    ),
    RecipeTuple(
        consumes={"Žula": 1},
        needs=("Kamenná palice"),
        creates={"Písek": 120}
    ),
    RecipeTuple(
        consumes={"Žula": 1, "Dřevěná palice": 1},
        creates={"Kamenná palice": 1}
    ),
    RecipeTuple(
        consumes={"Dřevěná palice": 1, "Žula": 1},
        creates={"Kladivo": 160}
    ),
    RecipeTuple(
        consumes={"Radix sort": 2, "Křemen": 10},
        needs=("Kladivo", "Kamenné dláto"),
        creates={"Robot": 1}
    ),
    RecipeTuple(
        consumes={"Proutěná ošatka": 3, "Quick sort": 2},
        creates={"Radix sort": 1}
    ),
    RecipeTuple(
        consumes={"Monolit": 1, "Rekurze": 5, "Bubble sort": 2},
        creates={"Quick sort": 1}
    ),
    RecipeTuple(
        consumes={"Mýdlo": 1, "Voda": 1, "Random sort": 2},
        creates={"Bubble sort": 1}
    ),
    RecipeTuple(
        consumes={"Kulaté kamínky na cvrnkání": 2},
        creates={"Random sort": 1}
    ),
    RecipeTuple(
        consumes={"Voda": 60, "Trilobajt": 1, "Med": 120},
        creates={"Lepicí kámen": 1}
    ),
    RecipeTuple(
        consumes={"Včelí plástev": 1},
        creates={"Med": 180}
    ),
    RecipeTuple(
        consumes={"Trilobit": 8},
        creates={"Trilobajt": 1}
    ),
]