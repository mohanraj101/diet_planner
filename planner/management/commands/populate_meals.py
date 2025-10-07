
# planner/management/commands/populate_meals.py
from django.core.management.base import BaseCommand
from planner.models import Meal

class Command(BaseCommand):
    help = 'Populate sample meals for the diet planner'

    def handle(self, *args, **options):
        Meal.objects.all().delete()
        data = [
            # Breakfast (veg)
            {'name':'Oats with milk', 'category':'breakfast','calories':320,'protein':12,'carbs':50,'fat':7,'is_veg':True},
            {'name':'Idli + Sambar (2 idli)', 'category':'breakfast','calories':250,'protein':8,'carbs':45,'fat':3,'is_veg':True},
            {'name':'Poha (1 plate)', 'category':'breakfast','calories':300,'protein':6,'carbs':55,'fat':5,'is_veg':True},
            {'name':'Vegetable Upma', 'category':'breakfast','calories':280,'protein':7,'carbs':52,'fat':6,'is_veg':True},
            # Lunch (veg + nonveg)
            {'name':'Rice + Dal + Sabzi', 'category':'lunch','calories':650,'protein':18,'carbs':95,'fat':12,'is_veg':True},
            {'name':'Chapati (2) + Vegetable Curry', 'category':'lunch','calories':550,'protein':14,'carbs':70,'fat':16,'is_veg':True},
            {'name':'Chicken Curry + Rice', 'category':'lunch','calories':700,'protein':35,'carbs':80,'fat':22,'is_veg':False},
            {'name':'Egg Curry + Chapati', 'category':'lunch','calories':600,'protein':30,'carbs':55,'fat':18,'is_veg':False},
            # Dinner
            {'name':'Chapati + Dal + Salad', 'category':'dinner','calories':500,'protein':16,'carbs':60,'fat':12,'is_veg':True},
            {'name':'Veg Khichdi', 'category':'dinner','calories':450,'protein':12,'carbs':70,'fat':8,'is_veg':True},
            {'name':'Chicken Grilled + Veg', 'category':'dinner','calories':520,'protein':40,'carbs':30,'fat':18,'is_veg':False},
            {'name':'Soup + Salad + Bread', 'category':'dinner','calories':350,'protein':10,'carbs':40,'fat':10,'is_veg':True},
            # Snacks
            {'name':'Fruit Salad', 'category':'snack','calories':120,'protein':2,'carbs':30,'fat':0.5,'is_veg':True},
            {'name':'Nuts (small handful)', 'category':'snack','calories':200,'protein':6,'carbs':8,'fat':18,'is_veg':True},
            {'name':'Yogurt (cup)', 'category':'snack','calories':150,'protein':8,'carbs':12,'fat':4,'is_veg':True},
            {'name':'Boiled Eggs (2)', 'category':'snack','calories':160,'protein':12,'carbs':2,'fat':11,'is_veg':False},
        ]
        for m in data:
            Meal.objects.create(**m)
        self.stdout.write(self.style.SUCCESS('Sample meals populated.'))
