from django.shortcuts import render

# Create your views here.

def home_page_view(request):
    # Context can be added here if the homepage needs dynamic data
    context = {}
    return render(request, 'home.html', context)
