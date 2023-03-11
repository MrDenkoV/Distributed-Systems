from flask import Flask, url_for, render_template, redirect, session, request
from forms import UserForm
from apis import APIS
import wtforms_json


app = Flask(__name__)
# app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "SECRET"
# app.config["CSRF"] = True
wtforms_json.init()


@app.route('/', methods=['POST', 'GET'])
def index():
    form = UserForm() if not request.is_json else UserForm.from_json(request.json)
    if form.validate_on_submit():
        session['form'] = request.form if not request.is_json else request.json
        session['to'] = request.form.getlist('to') if not request.is_json else list(request.json['to'].split(','))
        return redirect(url_for("results"))
    return render_template('form.html', form=form)


@app.route('/results')
def results():
    if 'form' not in session:
        print(request.form)
    ask = APIS.parse(session['form'], session['to'])
    ress = [APIS.send_req(res+ask[0]) for res in ask[1:]]
    # print("\n".join(ress))
    res = APIS.parse_res(ress)
    return render_template('results.html',
                            amount=res['amount'],
                            date=res['date'],
                            frm=res['from'],
                            rates=res['rates'])

app.run()
