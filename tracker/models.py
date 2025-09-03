from django.db import models
from decimal import Decimal
# Create your models here.



ASSET_CHOICES=(
    ('Stock', 'Stock'),
    ('Crypto', 'Crypto'),
)

class DateMixin(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class Asset(DateMixin):
    symbol=models.CharField(max_length=10)
    name= models.CharField(max_length=100)
    buy_price=models.DecimalField(max_digits=10, decimal_places=2)
    amount=models.DecimalField(max_digits=10, decimal_places=8)
    asset_type=models.CharField(max_length=50, choices=ASSET_CHOICES)
    owner=models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol

    

class PriceHistory(DateMixin):
    symbol=models.CharField(max_length=10,blank=True,null=True)
    # asset=models.ForeignKey(Asset, on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f" {self.price} on {self.created_at}"


CONDITION_CHOICES = (
    ('Above', 'Above'),
    ('Below', 'Below'),
)


class Alert(DateMixin):
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE)
    asset=models.ForeignKey(Asset, on_delete=models.CASCADE)
    target_price=models.DecimalField(max_digits=10, decimal_places=2)
    trigger=models.BooleanField(default=True)
    condition=models.CharField(max_length=10, choices=CONDITION_CHOICES)

    def __str__(self):
        return f"Alert for {self.asset.name} at {self.target_price}"
    


#we gon delete the asset after we sell it. we can only see the asset when we had already bought it

class Transaction(DateMixin):
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE)
    # asset=models.ForeignKey(Asset, on_delete=models.CASCADE,blank=True,null=True)
    transaction_type=models.CharField(max_length=10, choices=(('Buy','Buy'),('Sell','Sell')))
    price_per_unit=models.DecimalField(max_digits=10, decimal_places=2)
    amount=models.DecimalField(max_digits=10, decimal_places=8)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.transaction_type} at {self.price_per_unit}"
    

class Profile(DateMixin):
    user=models.OneToOneField('auth.User',on_delete=models.CASCADE)
    money=models.PositiveIntegerField(default=0)
    name=models.CharField(max_length=300,blank=True,null=True)

    def __str__(self):
        return self.name
    
    # def save(self):
    #     assets=Asset.objects.all()
    #     for asset in assets:
    #         prices=PriceHistory.objects.filter(symbol=asset.symbol.upper()).order_by('-created_at').first()
    #         if prices:
    #             amount=Decimal(asset.amount)
    #             price_per_unit=Decimal(prices.price)
    #             current=Decimal(price_per_unit)*Decimal(amount)
    #             self.money+=current

    #     super().save()





