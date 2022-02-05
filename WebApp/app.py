from asyncio import tasks
from crypt import methods
from distutils.log import debug
from pickle import FALSE
from urllib import request
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import pandas as pd
#from sqlalchemy import except_
from algorithm2 import Solve_Problem
import uuid
#import js2py


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Create Database Tables
class User_Entries(db.Model):
    #__tablename__ = 'user_entries'
    id = db.Column(db.String(200), primary_key=True)
    doctor = db.Column(db.String(200), nullable= False)
    operation_date = db.Column(db.DateTime, nullable=False)
    department_name = db.Column(db.String(200), nullable=False)
    operation_duration  = db.Column(db.Integer, nullable= False)
    operation_urgency = db.Column(db.Integer, nullable=False)
    operation_room = db.Column(db.String(200))

class Department_Info(db.Model):
    #__tablename__ = 'department_info'
    id = db.Column(db.String(200), primary_key=True)
    department_name = db.Column(db.String(200), nullable=False)
    department_capacity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Operation_rooms_Info(db.Model):
    #__tablename__ = 'operation_rooms_info'
    id = db.Column(db.String(200), primary_key=True)
    room_name = db.Column(db.String(200), nullable=False)
    room_capacity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)



    # def __repr__(self):
    #    return '<User entry %r is created>' %self.id

# Create all routes
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['submit_btn'] == 'submit_form':
            op_date = request.form['op_date']
            dep_name = request.form['dep_name']
            doctor_name = request.form['doctor_name']
            op_duration = request.form['op_duration']
            op_urgency = request.form['op_urgency']

            ####
            new_user_entry = User_Entries(
                            id=str(dep_name + '-' + str(uuid.uuid4())), 
                            doctor=doctor_name, 
                            operation_date=datetime.strptime(op_date, '%m/%d/%Y').date(), 
                            department_name=dep_name,
                            operation_duration=int(op_duration),
                            operation_urgency=int(op_urgency)
                            )

            
            ####
            # Change date format that user entered
            # date format should be same with DB 
            # so that we can filter the date from DB
            op_date_formatted = datetime.strptime(request.form['op_date'], '%m/%d/%Y')

            # Bring two tables from DB
            departments_info = Department_Info.query.filter(Department_Info.date==op_date_formatted).all()
            operation_rooms_info = Operation_rooms_Info.query.filter(Operation_rooms_Info.date==op_date_formatted).all()
            #print(type(operation_rooms_info))
            #print(operation_rooms_info, departments_info)

            ####
            # If none of them is empty, add them into Solve_Problem class
            if len(departments_info)!=0 and len(operation_rooms_info)!=0:
                try:
                    # Save new user entry into DB
                    db.session.add(new_user_entry)
                    db.session.commit()
                    # Bring user entry from DB
                    user_entries = User_Entries.query.filter(User_Entries.operation_date==op_date_formatted).all()

                    #basket = pd.DataFrame(user_entries= user_entries.transpose(), columns=['id','doctor','operation_date','department_name','operation_duration','operation_urgency','operation_room'])
                    #print(basket)
                    
                    # Call  Solve_Problem class and give all tables as arguments
                    algorithm = Solve_Problem() 
                    possible_to_add = algorithm.get_ops(op_date_formatted, user_entries, departments_info, operation_rooms_info)                       
                    if  possible_to_add == 'not possible':
                        user_entry_to_delete = User_Entries.query.get_or_404(new_user_entry.id)
                        try:
                            db.session.delete(user_entry_to_delete)
                            db.session.commit()
                        except:
                            return 'There was a problem deleting that'

                        return render_template('alert.html')
                    else:
                        # Drop all entries in the given date from DB
                        entries_to_delete = User_Entries.query.filter(User_Entries.operation_date==op_date_formatted).all()
                        try:
                            db.session.delete(entries_to_delete)
                            db.session.commit()                       
                        except:
                            return 'There was a problem deleting user entries'
                        
                        # then add new updated entries from Solve_Problem.get_ops() method
                        try:
                            db.session.add(possible_to_add)
                            db.session.commit()
                        except:
                            return 'There was a problem adding updated user entries'
                        
                        return redirect('/')
                except:
                    print('There was an issue adding new user entry')
                    raise 
            else:
                # Create new alert page to inform a user to fill empty tables
                return render_template('alert2.html')


                 
        
        elif request.form['submit_btn'] == 'filter':
            filtered_date = datetime.strptime(request.form['filter_date'], '%m/%d/%Y')
            print(filtered_date)
            filtered_entries = User_Entries.query.filter(User_Entries.operation_date==filtered_date).all()
            print(f'filtered entries:{filtered_entries}')
            return render_template('index.html', tasks=filtered_entries)
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


@app.route('/admin', methods=['GET', 'POST'])
def show_tables():
    if request.method == 'POST':
        if request.form['submit_btn2'] == 'submit_form2':
            date = request.form['date']
            dep_name = request.form['dep_name']
            dep_capacity = request.form['dep_capacity']
            
            new_department_info = Department_Info(
                    id=str(dep_name + '-' + str(uuid.uuid4())),
                    date=datetime.strptime(date, '%m/%d/%Y').date(), 
                    department_name=dep_name,
                    department_capacity=int(dep_capacity), 
                    )
            try:
                db.session.add(new_department_info)
                db.session.commit()
                return redirect('/admin')
            except:
                print('There was an issue adding new user entry')
                raise
        
        elif request.form['submit_btn2'] == 'filter':
            filtered_date = datetime.strptime(request.form['filter_date'], '%m/%d/%Y')
            filtered_entries = Department_Info.query.filter(Department_Info.date==filtered_date).all()
            return render_template('admin.html', departments=filtered_entries)
    else:
        department_info = Department_Info.query.order_by(Department_Info.date).all()
        return render_template('admin.html', departments=department_info)

@app.route('/admin/delete/<id>')
def admin_delete(id):
    department_info_to_delete = Department_Info.query.get_or_404(id)
    try:
        db.session.delete(department_info_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'There was a problem deleting that'

@app.route('/result', methods=['GET'])
def optimize():
    entries = User_Entries.query.order_by(User_Entries.operation_date).all()
    results = Solve_Problem()
    return render_template('result.html', tasks=entries)

@app.route('/rooms', methods=['GET', 'POST'])
def get_rooms():
    if request.method == 'POST':
        if request.form['submit_btn3'] == 'submit_form3':
            date = request.form['date']
            room_name = request.form['room_name']
            room_capacity = request.form['room_capacity']
            
            new_room_info = Operation_rooms_Info(
                    id=str(room_name + '-' + str(uuid.uuid4())),
                    date=datetime.strptime(date, '%m/%d/%Y').date(), 
                    room_name=room_name,
                    room_capacity=int(room_capacity), 
                    )
            try:
                db.session.add(new_room_info)
                db.session.commit()
                return redirect('/rooms')
            except:
                print('There was an issue adding new user entry')
                raise
        
        elif request.form['submit_btn3'] == 'filter':
            filtered_date = datetime.strptime(request.form['filter_date'], '%m/%d/%Y')
            filtered_entries = Operation_rooms_Info.query.filter(Operation_rooms_Info.date==filtered_date).all()
            return render_template('room.html', rooms=filtered_entries)
    else:
        rooms_info = Operation_rooms_Info.query.order_by(Operation_rooms_Info.date).all()
    return render_template('room.html', rooms = rooms_info)

@app.route('/rooms/delete/<id>')
def delete_op_rooms(id):
    op_room_info_to_delete = Operation_rooms_Info.query.get_or_404(id)
    try:
        db.session.delete(op_room_info_to_delete)
        db.session.commit()
        return redirect('/rooms')
    except:
        return 'There was a problem deleting that'


if __name__ == '__main__':
    app.run(debug=True)

