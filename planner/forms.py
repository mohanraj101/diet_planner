# planner/forms.py
from django import forms

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'placeholder':'Your name'}))
    age = forms.IntegerField(min_value=10, max_value=120, initial=25)
    gender = forms.ChoiceField(choices=[('male','Male'),('female','Female')])
    height = forms.FloatField(help_text='cm', initial=170)
    weight = forms.FloatField(help_text='kg', initial=65)
    activity = forms.ChoiceField(choices=[
        ('1.2','Sedentary (little exercise)'),
        ('1.375','Light (1-3 days/week)'),
        ('1.55','Moderate (3-5 days/week)'),
        ('1.725','Active (6-7 days/week)'),
    ])
    food_pref = forms.ChoiceField(choices=[('veg','Vegetarian'),('nonveg','Non-vegetarian')])
    goal = forms.ChoiceField(choices=[('lose','Lose weight'),('maintain','Maintain weight'),('gain','Gain weight')])
    # New: health conditions (optional)
    CONDITIONS = [
        ('diabetes','Diabetes (low sugar)'),
        ('elderly','Elderly / Age 60+ (protein focused)'),
        ('digestion','Digestion issues / IBS (low fat)'),
        ('high_protein','High protein requirement'),
    ]
    conditions = forms.MultipleChoiceField(
        choices=CONDITIONS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select any health constraints (optional)'
    )