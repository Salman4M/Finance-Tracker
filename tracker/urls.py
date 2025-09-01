from django.urls import path

from tracker import views
urlpatterns = [
    path('asset/<str:symbol>/', views.asset_price_history_list_view, name='asset_price_history_list'),
]
