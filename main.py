from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,HiddenField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[str] = mapped_column(String(250), nullable=False)
    wifi: Mapped[str] = mapped_column(String(250), nullable=False)
    power: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe location on Google Maps (URL)', validators=[DataRequired()])
    rating = SelectField('Cafe Rating', choices=["✘", "☕", "☕☕", "☕☕☕", "☕☕☕☕"], validators=[DataRequired()])

    wifi = SelectField('Wifi Strength Rating', choices=['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪'], validators=[DataRequired()])

    power = SelectField('Power Socket Availability', choices=['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌'], validators=[DataRequired()])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    cafe_id = HiddenField('Cafe Id')
    submit = SubmitField('Delete')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            location=form.location.data,
            rating=form.rating.data,
            wifi=form.wifi.data,
            power=form.power.data
        )
        db.session.add(cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with app.app_context():
        result = db.session.execute(db.select(Cafe))
        all_cafes = result.scalars().all()

    delete_form = DeleteForm()

    return render_template('cafes.html', cafes=all_cafes, delete_form=delete_form)


@app.route('/delete/<int:cafe_id>', methods=['POST'])
def delete_cafe(cafe_id):
    form = DeleteForm()
    if form.validate_on_submit():
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return redirect(url_for('cafes'))

@app.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
def edit(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    form = CafeForm(obj=cafe)
    if form.validate_on_submit():
        form.populate_obj(cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template("edit.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)
