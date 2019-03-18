from django.shortcuts import render_to_response, render



def index(request):
    return render_to_response("index.html", {})


def about(request):
    return render_to_response("about.html", {})
