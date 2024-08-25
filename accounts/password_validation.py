from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomLengthValidator:
    def __init__(self, min_length=8, max_length=16):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, password, user=None):
        if len(password) > self.max_length or len(password) < self.min_length:
            raise ValidationError(
                _("%(min_length)d자 이상 %(max_length)d자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다."),
                code="password_length_is_incorrect",
                params={"min_length": self.min_length, "max_length": self.max_length},
            )
    
    def get_help_text(self):
        return _(
            "%(min_length)d자 이상 %(max_length)d자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다."
            % {"min_length": self.min_length, "max_length": self.max_length}
        )
    
class SymbolValidator:
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("8자 이상 16자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다.!!"),
                code="password_no_symbol",
            )
    def get_help_text(self):
        return _(
            "8자 이상 16자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다."
        )

class UpperLowerValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Za-z]', password):
            raise ValidationError(
                _("8자 이상 16자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다.!"),
                code='password_no_letter',
            )

    def get_help_text(self):
        return _(
            "8자 이상 16자 이하, 한 개 이상의 숫자/영어/특수문자를 포함해야 합니다."
        )