# op_room_opt
Authors: Kültigin Bozdemir & Shirvan Hashimov <br>
<br>
This is  an optimization study that aims to maximize the usage of operations room at a hospital.
The hospital has multiple op rooms that serve for multiple departments at the hospital. Every department has a daily capacity in minutes due to the available staff.<br>
The operation rooms are also available for a limited time in a day. Departments register the operations at a central planning server. Operations have a urgency attribute that refers the value of an operation. <br>
Please watch the video for the further explaination. https://hochschule-rhein-waal.sciebo.de/s/Z25MLnIfCrv5Mbg <br>
The project has two stages. First stage is to implement an optimization algorith to solve the problem. The problem is almost identical to knapsack problem. 
Pyomo with open-source solvers has already been used to solve this integer programing. 
At the second stage, Shirvan Hashimov, one of Operations Research Club members,  has developed an interface and corresponding database to allow the users at the hospital to easily communicate with the solver. <br>
This repository contains all packages. Please run run_py.ipynb file in Jupyter. If the browers does not show, click on your localhost address on the output section on the Jupyter file. 
<br>
Please see the or_club_krankenhaus.pdf file for the explnations about the problem and the solution. <br>
<br>

<img width="933" alt="image" src="https://user-images.githubusercontent.com/56939663/160475523-c5c3cdf4-0141-4785-b229-bfe1df8f8161.png">

<img width="470" alt="image" src="https://user-images.githubusercontent.com/56939663/160475952-d0d8f0cb-9025-41b0-88cc-cb37f1f9bfba.png">
<img width="410" alt="image" src="https://user-images.githubusercontent.com/56939663/160475988-f22f1f7d-46ca-4067-ba39-761884d823a3.png">
<img width="569" alt="image" src="https://user-images.githubusercontent.com/56939663/160476025-fb683e65-987c-4885-a8b1-8bf5bd15c6d0.png">
