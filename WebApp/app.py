from asyncio import tasks
from crypt import methods
from distutils.log import debug
from pickle import FALSE
from urllib import request
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from algorithm import solve_knapsack_problem
import uuid


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User_Entries(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    doctor = db.Column(db.String(200), nullable= False)
    operation_date = db.Column(db.String(200), nullable=False)
    department_name = db.Column(db.String(200), nullable=False)
    department_capacity = db.Column(db.Integer, nullable=False)
    operation_duration  = db.Column(db.Integer, nullable= False)
    operation_urgency = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User entry %r is created>' %self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        op_date = request.form['op_date']
        dep_name = request.form['dep_name']
        dep_capacity = request.form.get('dep_capacity')
        op_duration = request.form['op_duration']
        op_urgency = request.form['op_urgency']

        ####
        new_user_entry = User_Entries(
                        id=str(dep_name + '-' + str(uuid.uuid4())), 
                        doctor='John Doe', 
                        operation_date=op_date, 
                        department_name=dep_name,
                        department_capacity=int(dep_capacity), 
                        operation_duration=int(op_duration),
                        operation_urgency=int(op_urgency)
                        )

        try:
            db.session.add(new_user_entry)
            db.session.commit()
            return redirect('/')
        except:
            print('There was an issue adding new user entry')
            raise 
    else:
        entries = User_Entries.query.order_by(User_Entries.operation_date).all()
        return render_template('index.html', tasks=entries)


@app.route('/delete/<id>')
def delete(id):
    user_entry_to_delete = User_Entries.query.get_or_404(id)

    try:
        db.session.delete(user_entry_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that'

@app.route('/admin', methods=['GET'])
def show_tables():
    entries = User_Entries.query.order_by(User_Entries.operation_date).all()
    return render_template('tables.html', tasks=entries)

@app.route('/result', methods=['GET'])
def optimize():
    entries = User_Entries.query.order_by(User_Entries.operation_date).all()
    results = solve_knapsack_problem(entries)
    return render_template('result.html', tasks=entries)

if __name__ == '__main__':
    app.run(debug=True)