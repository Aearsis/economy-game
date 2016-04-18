from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse

from data.generating import *


@permission_required("control_game")
def index(request):
    r = generate_all_data()
    return HttpResponse("\n".join(r))
