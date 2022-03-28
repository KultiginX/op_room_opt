# op_room_opt
This is  an optimization study that aims to maximize the usage of operations room at a hospital.
The hospital has multiple op rooms that serve for multiple departments at the hospital. Every department has a daily capacity in minutes due to the available staff. 
The operation rooms are also available for a limited time in a day. Departments register the operations at a central planning server. Operations have a urgency attribute that refers the value of an operation. 
Please watch the video for the further explaination. https://hochschule-rhein-waal.sciebo.de/s/Z25MLnIfCrv5Mbg
The project has two stages. First stage is to implement an optimization algorith to solve the problem. The problem is almost identical to knapsack problem. 
Pyomo with open-source solvers has already been used to solve this integer programing. 
At the second stage, Shirvan Hashimov, one of Operations Research Club members,  has developed an interface and corresponding database to allow the users at the hospital to easily communicate with the solver. 
This repository contains all packages. Please run run run_py.ipynb file in Jupyter. If the browers does not show, click on your localhost address on the output section on the Jupyter file. 

