from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def restaurant_list(request):
    return render(request, 'restaurants/restaurant_list.html')