import pyomo.environ as pyo #install pyomo
# conda install -c conda-forge pyomo
# install glpk 
# conda install -c conda-forge glpk
import pandas as pd
import numpy as np

    
class Solve_Problem:
    ''' Pass date for the get_ops function. It gets the operations table on that particullar date from the sqlite db.
    Convert them and other necessary tables into pandas df. Those dataframes are passed into pyomo as decision variables and contsraints.
    Solver solves the problem. If the solution does not exclude any existing operation from the solution, it approves the last application and updates the table in the db.
    Otherwise, it returns only a warning that the registration can be done on that particular date. The table is not modified.'''
    
    def get_ops(self, date, user_entries, departments_info, operation_rooms_info):

        # operations
        table=[(str(e).split()[1].strip('>'),e.doctor, e.operation_date,e.department_name, e.operation_duration,e.operation_urgency, e.operation_room) for e in user_entries]
        table = pd.DataFrame(table)
        basket = pd.DataFrame(table, columns=['id','doctor','operation_date','department_name','operation_duration','operation_urgency','operation_room'])
        basket.set_index('id')

        #departments
        table2 =[(str(e).split()[1].strip('>'),e.department_name, e.department_capacity,e.date) for e in departments_info]
        dep_df=pd.DataFrame(table2, columns=['id','department_name','department_capacity','date'])
        dep_df = dep_df.set_index('id')
        dep_df['department_capacity']=dep_df['department_capacity'].astype(int)
        
        # operation rooms
        table3 =[(str(e).split()[1].strip('>'),e.room_name, e.room_capacity,e.date) for e in operation_rooms_info]
        op_df=pd.DataFrame(table3, columns=['id','room_name','room_capacity','date'])
        op_df = op_df.set_index('id')
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
        mdl.bin_cap = pyo.Param(mdl.bins, initialize= {row["room_name"]:row["room_capacity"] for i,row in op_df.iterrows()} )
        mdl.dep_cap = pyo.Param(mdl.deps, initialize= {row["department_name"]:row["department_capacity"] for i,row in dep_df.iterrows()}, mutable=True)



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

        
        if basket.index.isin(list(dic.keys())).all():
            basket['operation_room'] = basket.index.map(dic) 
            return basket

        else:
            return 'not possible'