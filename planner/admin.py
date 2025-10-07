# planner/admin.py
from django.contrib import admin
from .models import Meal, DietPlan

admin.site.register(Meal)
admin.site.register(DietPlan)