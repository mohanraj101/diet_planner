# planner/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileForm
from .models import Meal, DietPlan
import json, random
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

# Fallback meal list used when DB has no meals
FALLBACK_MEALS = [
    # breakfast
    {'name':'Oats with milk','category':'breakfast','calories':320,'protein':12,'carbs':50,'fat':7,'is_veg':True},
    {'name':'Idli + Sambar (2 idli)','category':'breakfast','calories':250,'protein':8,'carbs':45,'fat':3,'is_veg':True},
    {'name':'Poha (1 plate)','category':'breakfast','calories':300,'protein':6,'carbs':55,'fat':5,'is_veg':True},
    {'name':'Vegetable Upma','category':'breakfast','calories':280,'protein':7,'carbs':52,'fat':6,'is_veg':True},
    # lunch
    {'name':'Rice + Dal + Sabzi','category':'lunch','calories':650,'protein':18,'carbs':95,'fat':12,'is_veg':True},
    {'name':'Chapati (2) + Vegetable Curry','category':'lunch','calories':550,'protein':14,'carbs':70,'fat':16,'is_veg':True},
    {'name':'Chicken Curry + Rice','category':'lunch','calories':700,'protein':35,'carbs':80,'fat':22,'is_veg':False},
    {'name':'Egg Curry + Chapati','category':'lunch','calories':600,'protein':30,'carbs':55,'fat':18,'is_veg':False},
    # dinner
    {'name':'Chapati + Dal + Salad','category':'dinner','calories':500,'protein':16,'carbs':60,'fat':12,'is_veg':True},
    {'name':'Veg Khichdi','category':'dinner','calories':450,'protein':12,'carbs':70,'fat':8,'is_veg':True},
    {'name':'Chicken Grilled + Veg','category':'dinner','calories':520,'protein':40,'carbs':30,'fat':18,'is_veg':False},
    {'name':'Soup + Salad + Bread','category':'dinner','calories':350,'protein':10,'carbs':40,'fat':10,'is_veg':True},
    # snacks
    {'name':'Fruit Salad','category':'snack','calories':120,'protein':2,'carbs':30,'fat':0.5,'is_veg':True},
    {'name':'Nuts (small handful)','category':'snack','calories':200,'protein':6,'carbs':8,'fat':18,'is_veg':True},
    {'name':'Yogurt (cup)','category':'snack','calories':150,'protein':8,'carbs':12,'fat':4,'is_veg':True},
    {'name':'Boiled Eggs (2)','category':'snack','calories':160,'protein':12,'carbs':2,'fat':11,'is_veg':False},
]

def index(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            weight = data['weight']
            height = data['height']
            age = data['age']
            gender = data['gender']
            activity = float(data['activity'])
            goal = data['goal']
            food_pref = data['food_pref']
            conditions = data.get('conditions', []) or []

            # Mifflin-St Jeor BMR
            if gender == 'male':
                bmr = 10*weight + 6.25*height - 5*age + 5
            else:
                bmr = 10*weight + 6.25*height - 5*age - 161

            tdee = bmr * activity
            if goal == 'lose':
                target = max(1200, tdee - 500)
            elif goal == 'gain':
                target = tdee + 300
            else:
                target = tdee

            plan = generate_weekly_plan(target, food_pref, conditions, age)
            summary = compute_summary(plan)
            dp = DietPlan.objects.create(
                name = data['name'],
                profile_json = json.dumps({'bmr': round(bmr,1),'tdee': round(tdee,1),'target_cal': int(round(target)), 'conditions': conditions, 'age': age}),
                plan_json = json.dumps({'plan': plan, 'summary': summary})
            )
            return redirect('view_plan', plan_id=dp.id)
    else:
        form = ProfileForm()
    return render(request, 'index.html', {'form': form})


def generate_weekly_plan(daily_target, food_pref, conditions, age):
    """
    Build a 7-day plan using DB meals if present, otherwise FALLBACK_MEALS.
    Conditions is a list like ['diabetes', 'elderly', ...]
    """
    veg_only = (food_pref == 'veg')
    categories = ['breakfast','lunch','dinner','snack']
    proportions = {'breakfast':0.25, 'lunch':0.35, 'dinner':0.30, 'snack':0.10}

    # Load meals from DB if any
    meals_qs = Meal.objects.all()
    meals_list = []
    if meals_qs.exists():
        if veg_only:
            meals_qs = meals_qs.filter(is_veg=True)
        for m in meals_qs:
            meals_list.append({
                'id': m.id,
                'name': m.name,
                'category': m.category,
                'calories': m.calories,
                'protein': m.protein,
                'carbs': m.carbs,
                'fat': m.fat,
                'is_veg': m.is_veg
            })
    else:
        # use fallback
        meals_list = [dict(m) for m in FALLBACK_MEALS if (not veg_only) or m.get('is_veg', True)]

    # group by category
    cat_map = {c: [m for m in meals_list if m['category']==c] for c in categories}

    plan = {}
    for day in range(1,8):
        day_key = f"Day {day}"
        day_meals = {}
        for cat in categories:
            target_cal = max(30, int(daily_target * proportions[cat]))
            candidates = cat_map.get(cat, [])[:]  # copy

            # Apply condition-based filters
            # Diabetes -> avoid very high carbs
            if 'diabetes' in conditions:
                candidates = [c for c in candidates if c.get('carbs',0) <= 60]  # conservative threshold
            # Digestion issues -> avoid high fat items
            if 'digestion' in conditions:
                candidates = [c for c in candidates if c.get('fat',0) <= 16]
            # If elderly or age >= 60 or high protein -> prefer high protein
            prefer_protein = ('elderly' in conditions) or ('high_protein' in conditions) or (age >= 60)

            # If no candidates after filtering, revert to unfiltered category list (graceful)
            if not candidates:
                candidates = cat_map.get(cat, [])[:] or [ {'name':'N/A','calories':0,'protein':0,'carbs':0,'fat':0} ]

            # Ranking: if prefer_protein select those with higher protein (but within reasonable calorie range)
            if prefer_protein:
                # filter candidates close to target cal (±40%) then sort by protein desc, then cal diff
                close = [c for c in candidates if abs(c['calories'] - target_cal) <= max(80, int(0.4*target_cal))]
                if close:
                    candidates_sorted = sorted(close, key=lambda c: (-c.get('protein',0), abs(c['calories'] - target_cal)))
                else:
                    candidates_sorted = sorted(candidates, key=lambda c: (-c.get('protein',0), abs(c['calories'] - target_cal)))
            else:
                # Normal: prefer calorie closest to target
                candidates_sorted = sorted(candidates, key=lambda c: abs(c.get('calories',0) - target_cal))

            # pick one; randomize among top 3 for variety
            chosen = None
            if candidates_sorted:
                top = candidates_sorted[:3]
                chosen = random.choice(top)
            else:
                chosen = {'name':'N/A','calories':0,'protein':0,'carbs':0,'fat':0}

            day_meals[cat.capitalize()] = {
                'name': chosen.get('name','N/A'),
                'calories': int(chosen.get('calories',0)),
                'protein': float(chosen.get('protein',0)),
                'carbs': float(chosen.get('carbs',0)),
                'fat': float(chosen.get('fat',0))
            }
        plan[day_key] = day_meals

    return plan


def compute_summary(plan):
    total_cal = total_prot = total_carbs = total_fat = 0.0
    for day, meals in plan.items():
        for meal, info in meals.items():
            total_cal += info.get('calories',0)
            total_prot += info.get('protein',0)
            total_carbs += info.get('carbs',0)
            total_fat += info.get('fat',0)
    avg_daily_cal = round(total_cal / 7, 1) if total_cal else 0.0
    return {
        'weekly_calories': int(total_cal),
        'avg_daily_calories': avg_daily_cal,
        'total_protein': round(total_prot,1),
        'total_carbs': round(total_carbs,1),
        'total_fat': round(total_fat,1)
    }


def view_plan(request, plan_id):
    dp = get_object_or_404(DietPlan, id=plan_id)
    data = json.loads(dp.plan_json)
    profile = json.loads(dp.profile_json)
    return render(request, 'plan.html', {'plan': data['plan'], 'summary': data['summary'], 'profile': profile, 'dp': dp})


def history(request):
    plans = DietPlan.objects.order_by('-created_at')[:20]
    return render(request, 'history.html', {'plans': plans})

# ---------- PDF export (same as before) ----------
def export_pdf(request, plan_id):
    dp = get_object_or_404(DietPlan, id=plan_id)
    data = json.loads(dp.plan_json)
    profile = json.loads(dp.profile_json)
    context = {'plan': data['plan'], 'summary': data['summary'], 'profile': profile, 'dp': dp}
    html = render_to_string('plan_pdf.html', context)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)
    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="diet_plan_{dp.id}.pdf"'
    return response

# ---------- Swap meal endpoint (same as before) ----------
def swap_meal(request, plan_id, day_index, meal_key):
    dp = get_object_or_404(DietPlan, id=plan_id)
    data = json.loads(dp.plan_json)
    cat_map = {'Breakfast': 'breakfast','Lunch':'lunch','Dinner':'dinner','Snack':'snack'}
    category = cat_map.get(meal_key, 'lunch')

    if request.method == 'POST':
        new_meal_id = int(request.POST.get('meal_id'))
        try:
            new_meal = Meal.objects.get(id=new_meal_id)
            day_key = f"Day {day_index}"
            if 'plan' in data and day_key in data['plan']:
                data['plan'][day_key][meal_key] = {
                    'name': new_meal.name,
                    'calories': new_meal.calories,
                    'protein': new_meal.protein,
                    'carbs': new_meal.carbs,
                    'fat': new_meal.fat
                }
                data['summary'] = compute_summary(data['plan'])
                dp.plan_json = json.dumps(data)
                dp.save()
        except Meal.DoesNotExist:
            pass
        return redirect('view_plan', plan_id=dp.id)

    candidate_meals = Meal.objects.filter(category=category).order_by('calories')
    return render(request, 'swap.html', {'dp': dp, 'day_index': day_index, 'meal_key': meal_key, 'candidates': candidate_meals})