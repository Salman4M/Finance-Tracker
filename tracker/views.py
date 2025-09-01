from django.shortcuts import render
from tracker.models import PriceHistory
# Create your views here.


def asset_price_history_list_view(request,symbol):
    price_history=PriceHistory.objects.filter(symbol=symbol.upper()).order_by('-created_at')
    context={
        'price_history':price_history
    }
    return render(request,'asset_price_history.html',context)


    