from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectMultipleField, SelectField, DecimalField, DateField
from wtforms.validators import ValidationError
from datetime import date
from apis import APIS
from decimal import ROUND_HALF_UP
import wtforms_json


class SelectMultipleFields(SelectMultipleField):
    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ",".join(valuelist)
        else:
            self.data = ""

class UserForm(FlaskForm):
    class Meta:
        csrf = False
    wtforms_json.init()
    curs = APIS.get_currencies().items()
    amount = DecimalField("Amount", places=2, rounding=ROUND_HALF_UP, default=1)
    fr = SelectField("From", choices=curs, default='PLN')
    to = SelectMultipleFields("To", choices=curs)
    dat = DateField("When", default=date.today())
    submit = SubmitField("Submit")
