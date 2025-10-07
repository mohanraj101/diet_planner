
# planner/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plan/<int:plan_id>/', views.view_plan, name='view_plan'),
    path('history/', views.history, name='history'),
    path('plan/<int:plan_id>/pdf/', views.export_pdf, name='export_pdf'),
    path('plan/<int:plan_id>/swap/<int:day_index>/<str:meal_key>/', views.swap_meal, name='swap_meal'),
]
