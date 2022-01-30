from django.shortcuts import render

# Create your views here.
def index_view(request):
    return render(request, 'board/index.html', context={'main_color_card1': 'bg-red-100', 'main_color_card2': 'bg-yellow-700', 'main_color_card3': 'bg-green-600'})

def about(request):
    return render(request, 'board/about.html')
