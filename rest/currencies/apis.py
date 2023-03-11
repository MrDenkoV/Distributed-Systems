import requests
from datetime import date, timedelta, datetime

class APIS:
    web = "https://api.frankfurter.app/"
    keys = None
    
    @staticmethod
    def get_currencies():
        if not APIS.keys:
            APIS.keys = requests.get(APIS.web+'currencies').json()
        return APIS.keys


    @staticmethod
    def parse(form, to):
        ask = ""
        dat = None
        if form['amount'] != 0:
            ask += f"amount={form['amount']}&"
        ask += f"from={form['fr']}"
        if 'to' in form and len(to)>0 and (len(to)>1 or to[0]!=form['fr']):
            ask += f"&to={','.join(to)}"
        if datetime.strptime(form['dat'], "%Y-%m-%d").date() >= date.today():
            dat = "latest"
            askday = date.today()-timedelta(days=1)
        else:
            dat = str(form['dat'])
            askday = datetime.strptime(form['dat'], "%Y-%m-%d").date()-timedelta(days=1)
        askweek = askday-timedelta(days=6)
        askmonth = askday-timedelta(days=30)
        askyear = askday-timedelta(days=365)
        return ask, dat+'?', str(askday)+'?', str(askweek)+'?', str(askmonth)+'?', str(askyear)+'?'


    @staticmethod
    def send_req(req):
        return requests.get(APIS.web+req).json()


    @staticmethod
    def get_val(form, key, val):
        return form['rates'][key] if key in form['rates'] else val


    @staticmethod
    def parse_res(forms):
        res = dict()
        res['amount'] = forms[0]['amount']
        res['from'] = forms[0]['base']
        res['date'] = forms[0]['date']
        res['rates'] = dict()
        for key in forms[0]['rates']:
            val = forms[0]['rates'][key]
            res['rates'][key] = {
                'current': val,
                'day': round(APIS.get_val(forms[1], key, val)-val, 5),
                'week': round(APIS.get_val(forms[2], key, val)-val, 5),
                'month': round(APIS.get_val(forms[3], key, val)-val, 5),
                'year': round(APIS.get_val(forms[4], key, val)-val, 5),
            }
        # res['rates'] = forms[0]['rates']
        # for form, suf in zip(forms[1:], ["_day", "_week", "_month", "_year"]):
        #     for key, val in form['rates'].items():
        #         res['rates'][key+suf] = round(val - res['rates'][key], 5)
        return res
