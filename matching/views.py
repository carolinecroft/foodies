from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def discovery(request):
    return render(request, 'matching/discovery.html')


@login_required
def matches(request):
    return render(request, 'matching/matches.html')


@login_required
def compatibility(request):
    return render(request, 'matching/compatibility.html')