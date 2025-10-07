# planner/models.py
from django.db import models

class Meal(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast','Breakfast'),
        ('lunch','Lunch'),
        ('dinner','Dinner'),
        ('snack','Snack'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    calories = models.IntegerField()
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.calories} kcal"


class DietPlan(models.Model):
    name = models.CharField(max_length=120)
    profile_json = models.TextField()
    plan_json = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.id} - {self.name} - {self.created_at:%Y-%m-%d %H:%M}"