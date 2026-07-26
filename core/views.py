from django.shortcuts import render


def landing(request):
    return render(request, "core/landing.html")


def about(request):
    return render(request, "core/about.html")
