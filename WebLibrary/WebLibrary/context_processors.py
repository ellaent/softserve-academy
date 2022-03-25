from django.conf import settings
from .forms import ModeratorChoiceForm


def base_data(request):
    data = {}
    # MyForm(request.GET, user=request.user)
    data["mod_form"] = ModeratorChoiceForm()
    return data