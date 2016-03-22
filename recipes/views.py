from django.shortcuts import render, render_to_response


def index(request):
    return render_to_response("recipes/index.html")
