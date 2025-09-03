from django.shortcuts import render,redirect
from tracker.models import PriceHistory,Asset
# Create your views here.
from tracker.forms import BuyAssetForm,AlertForm
from decimal import Decimal


def asset_price_history_list_view(request,symbol):
    price_history=PriceHistory.objects.filter(symbol=symbol.upper()).order_by('-created_at')
    context={
        'price_history':price_history
    }
    return render(request,'asset_price_history.html',context)



def latest_crypto_price_list_view(request):
    symbols=PriceHistory.objects.filter(symbol__in=['BITCOIN','ETHEREUM']).values_list('symbol',flat=True).distinct()
    latest_prices=[]
    for symb in symbols:
        b=PriceHistory.objects.filter(symbol=symb).order_by('-created_at').first()
        if b:
            latest_prices.append(b)

    context={
        'latest_prices':latest_prices
    }
    return render(request,'latest_crypto_prices.html',context)



def buy_asset_view(request):
    form =BuyAssetForm()

    if request.method=='POST':
        form=BuyAssetForm(request.POST or None)

        if form.is_valid():
            asset=form.save(commit=False)
            asset.owner=request.user
            latest_price=PriceHistory.objects.filter(symbol=asset.symbol.upper()).order_by('-created_at').first()
            if latest_price:
                amount=Decimal(asset.amount)
                price_per_unit=Decimal(latest_price.price)

            price=amount*price_per_unit
            asset.buy_price=price   
            asset.save()
            return redirect('tracker:asset_detail', id=asset.id)
        

    return render(request,'buy_asset.html',{'form':form})

def sell_asset_view(request,id):
    asset=Asset.objects.get(id=id)
    if asset:
        if request.method=='POST':
            asset.delete()
            return redirect('tracker:latest_crypto_price_list')
    
    return render(request,'sell_asset.html',{"asset":asset})


def asset_detail_view(request,id):
    asset=Asset.objects.get(id=id)
    latest_price=PriceHistory.objects.filter(symbol=asset.symbol.upper()).order_by('-created_at').first()
    if latest_price:
        amount=Decimal(asset.amount)
        price_per_unit=Decimal(latest_price.price)

    price=amount*price_per_unit

    context={
        'asset':asset,
        'current_price':price
    }

    return render(request,'asset_detail.html',context)

from tracker.tasks import get_latest_prices


def asset_list_view(request):
    current_prices={}
    assets=Asset.objects.filter(owner=request.user)

    for asset in assets:
        price=PriceHistory.objects.filter(symbol=asset.symbol.upper()).order_by('-created_at').first()
        if price:
            amount=Decimal(asset.amount)
            price_per_unit=Decimal(price.price)
            current=Decimal(price_per_unit)*Decimal(amount)
            current_prices[asset.symbol]=current


    context={"assets":assets,"current_prices":current_prices}
    return render(request,'asset_list.html',context)

def create_alert_for_asset_view(request):
    form=AlertForm()

    if request.method=='POST':
        form=AlertForm(request.POST or None)

        if form.is_valid():
            alert=form.save(commit=False)
            alert.user=request.user
            alert.save()

            return redirect('tracker:asset_detail', id=alert.asset.id)

    return render(request,'create_alert.html',{'form':form})


def sell_asset_view(request, id):
    asset = Asset.objects.get(id=id)
    if request.method == 'POST':
        asset.delete()
        return redirect('tracker:asset_list')

    return render(request, 'sell_asset.html', {'asset': asset})


