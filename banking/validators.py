from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date

def validate_pesel(pesel : str):
    if not pesel.isdigit() or len(pesel) != 11:
        raise ValidationError(_("PESEL must consist of 11 digits"), code="consist")
    
    wage_factors = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
    digit = int(str(sum(int(i) * j for i, j in zip(pesel, wage_factors)))[-1]) # last_digit_of_control_sum
    control_digit = (10 - digit) if digit != 0 else 0
    if pesel[10] != str(control_digit):
        raise ValidationError(_("Incorrect PESEL"), code="invalid")
    return True
    
def validate_date_birth_above_18_today(date_birth: date):
    today = date.today()
    if today.year - date_birth.year > 18:
        return
    if today.year - date_birth.year == 18 and today.month > date_birth.month:
        return
    if today.year - date_birth.year == 18 and today.month == date_birth.month and today.day >= date_birth.day:
        return
    raise ValidationError(_("Required age above 18"), code="required_age")

def validate_pesel_match_birth_date(pesel, date_birth):
    month_to_year = {"0":"19","1":"19","2":"20","3":"20","4":"21","5":"21","6":"22","7":"22","8":"18","9":"18"}
    month = pesel[2:4]
    day = pesel[4:6]
    year = month_to_year[month[0]] + pesel[0:2]
    return int(year) == date_birth.year and int(day) == date_birth.day and int(month) % 20 == date_birth.month