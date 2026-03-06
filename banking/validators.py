from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, date

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
    if date.today() - date_birth < timedelta(days=365*18):
        raise ValidationError(_("Required age above 18"), code="required_age")
