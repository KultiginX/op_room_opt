import pyomo.environ as pyo #install pyomo
# conda install -c conda-forge pyomo
# install glpk 
# conda install -c conda-forge glpk
import pandas as pd

import sqlite3


class Solve_Problem:
    ''' Pass date for the get_ops function. It gets the operations table on that particullar date from the sqlite db.
    Convert them and other necessary tables into pandas df. Those dataframes are passed into pyomo as decision variables and contsraints.
    Solver solves the problem. If the solution does not exclude any existing operation from the solution, it approves the last application and updates the table in the db.
    Otherwise, it returns only a warning that the registration can be done on that particular date. The table is not modified.'''
    
    def __init__(self):
        
        self.solutions = []    # creates a new empty list for each day


    def get_ops(self, date):
        db = sqlite3.connect('/Users/shirvanhashimov/Desktop/Master/AppliedResearchProjectA/Website/test2.db') # change the path
        cnx = db 
        query = ''.join(['SELECT * FROM user__entries WHERE operation_date==',str(date)])# change name of the table.  save them with date in db. 

        basket = pd.read_sql(query,cnx)
        #basket.index=basket.id
        print(basket)

        query_dep_cap =''.join(['SELECT * FROM department__info WHERE date==',str(date)]) # table of department capacities
        dep_df = pd.read_sql_query(query_dep_cap, db)# departments
        dep_df.index=dep_df.department_name
        dep_df['department_capacity']=dep_df['department_capacity'].astype(int)



        query_op_cap = ''.join(['SELECT * FROM operation_rooms__info WHERE date==',str(date)]) # table of operation room capacities

        op_df = pd.read_sql_query(query_op_cap, db)# operations room
        op_df.index=op_df.room_name
        op_df['room_capacity']=op_df['room_capacity'].astype(int)
        
        # multi-knapsack, integer divisible

        mdl = pyo.ConcreteModel()

        # make sure id is also index in database user__entries
        mdl.invs = pyo.Set(initialize=list(zip(basket.index, basket["department_name"])))
        mdl.bins = pyo.Set(initialize=list(op_df.room_name)) ## list of operations room from db
        mdl.deps = pyo.Set(initialize=list(dep_df.department_name)) # list of departments from db

        # params
        mdl.value   = pyo.Param(mdl.invs, initialize= {(i,row["department_name"]):row["operation_urgency"] for i,row in basket.iterrows()} )
        mdl.weight  = pyo.Param(mdl.invs, initialize= {(i,row["department_name"]):row["operation_duration"] for i,row in basket.iterrows()})
        mdl.bin_cap = pyo.Param(mdl.bins, initialize= {i:row["room_capacity"] for i,row in op_df.iterrows()} )
        mdl.dep_cap = pyo.Param(mdl.deps, initialize= {i:row["department_capacity"] for i,row in dep_df.iterrows()}, mutable=True)



        # vars
        mdl.X = pyo.Var(mdl.invs, mdl.bins, within=pyo.Binary)     # the amount from invoice i in bin j



        ### Objective ###

        mdl.OBJ = pyo.Objective(expr=sum(mdl.X[i, b]*mdl.value[i] for 
                                i in mdl.invs for
                                b in mdl.bins), sense=pyo.maximize)


        ### constraints ###

        # don't overstuff bin
        def bin_limit(self, b):
            return sum(mdl.X[i, b]*mdl.weight[i] for i in mdl.invs) <= mdl.bin_cap[b]
        mdl.bin_limit = pyo.Constraint(mdl.bins, rule=bin_limit)

        # one_item can be only in a single op room.
        def one_item(self, i,d):
            return sum(mdl.X[i,d,b] for b in mdl.bins) <=1
        mdl.one_item = pyo.Constraint(mdl.invs, rule=one_item)



        # department limits

        mdl.dep_limits=pyo.ConstraintList()

        for d in mdl.deps:
            d_list=[]
            for i in mdl.X:
                if d==i[1]:
                    d_list.append(i)    
            mdl.dep_limits.add(expr=(sum(mdl.X[i]*mdl.weight[i[:2]] for i in d_list)<=mdl.dep_cap[d])) 



        # solve it...
        solver = pyo.SolverFactory('glpk')
        results = solver.solve(mdl)

        # save the output into dictionary


        dic=dict()

        for i in mdl.X:
            if pyo.value(mdl.X[i])==1:
                dic[i[0]]=i[2]

        #print(dic.keys())
        #print('basket', basket.index)
        if basket.index.isin(list(dic.keys())).all():
            #print(basket.tail(1).index, 'is registered')
            basket['operation_room'] = basket.index.map(dic)
            self.solutions.append(basket)
            #basket.to_sql('Result3',cnx, if_exists='append',index=True)
            query = ''.join(['DELETE FROM user__entries WHERE operation_date==',str(date)])# change name of the table.  save them with date in db. 
            db.engine.execute(query)
            basket.to_sql('user__entries',db, if_exists='append',index=False)
            
            db.session.commit()
            return 'possible'

        else:
            #print(basket.tail(1).index ,'is NOT registered')
            self.solution.append('Not possible')
            return 'not possible' 


