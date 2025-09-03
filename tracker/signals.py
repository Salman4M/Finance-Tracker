from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver


from tracker.models import PriceHistory, Asset, Transaction,Profile
from decimal import Decimal

### if asset is created when we buy some crypto it is what it is then
@receiver(post_save,sender=Asset)
def create_transaction_on_asset_buy(sender,instance,created,**kwargs):
    if created:
        latest_price=PriceHistory.objects.filter(symbol=instance.symbol.upper()).order_by('-created_at').first()
        if latest_price:
            amount=Decimal(instance.amount)
            price_per_unit=Decimal(latest_price.price)
            price=amount*price_per_unit
            Transaction.objects.create(
                user=instance.owner,
                price_per_unit=price_per_unit,
                transaction_type='Buy',
                amount=amount,
                total_price=price
            )

@receiver(pre_delete,sender=Asset)
def create_transaction_on_asset_sell(sender,instance,**kwargs):
    if  instance:
        latest_price=PriceHistory.objects.filter(symbol=instance.symbol.upper()).order_by('-created_at').first()
        if latest_price:
            amount=Decimal(instance.amount)
            price_per_unit=Decimal(latest_price.price)
            price=amount*price_per_unit
            Transaction.objects.create(
                user=instance.owner,
                price_per_unit=price_per_unit,
                transaction_type='Sell',
                amount=amount,
                total_price=price
            )




@receiver(post_save,sender='auth.User')
def create_profile_view(sender,instance,created,**kwargs):
     assets=Asset.objects.all()
     money=0
     for asset in assets:
        price=PriceHistory.objects.filter(symbol=asset.symbol.upper()).order_by('-created_at').first()
        if price:
            amount=Decimal(asset.amount)
            price_per_unit=Decimal(price.price)
            current=Decimal(price_per_unit)*Decimal(amount)
            money+=current

            if created:
                Profile.objects.create(user=instance,money=money)