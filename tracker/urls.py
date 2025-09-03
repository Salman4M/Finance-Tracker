from django.urls import path

app_name='tracker'

from tracker import views
urlpatterns = [
    path('asset/<str:symbol>/', views.asset_price_history_list_view, name='asset_price_history_list'),
    path('crypto/latest/', views.latest_crypto_price_list_view, name='latest_crypto_price_list'),
    path('buy/', views.buy_asset_view, name='buy_asset'),
    path('sell/<int:id>/',views.sell_asset_view,name='sell-asset'),
    path('asset/detail/<int:id>/', views.asset_detail_view, name='asset_detail'),
    path('alert/create/', views.create_alert_for_asset_view, name='create_alert'),
    path('assets/', views.asset_list_view, name='asset_list'),
]
