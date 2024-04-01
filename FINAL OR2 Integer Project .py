#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import docplex.mp as mp
from docplex.mp.model import Model


# In[35]:


class OR2_Integer_Project:
    def __init__(self):
        self.model=Model(name='OR2 Integer Project')
        
        #Set type of Candies and Worker Types
        self.candy_name=['Fruity Fun',"Chocolate Craze","Tis the Season"]
        self.worker_job=["Line Workers Required at:", "Technicians Required at:", "Supervisors Required at:", "Engineers Required at:"]
        
        #Demand Requirements in Arrays
        self.plant1_demand= [[50,58,40,35,30,37,45,48,35,36,40,44],
                        [6,8,5,5,4,5,6,6,7,8,7,6],
                        [10,9,10,12,15,15,10,8,9,9,16,12],
                        [7,9,6,8,6,5,8,7,6,7,6,4]]
        self.plant2_demand= [[30,38,40,36,40,37,45,48,43,36,43,38],
                        [7,6,7,6,5,6,5,6,5,7,8,5],
                        [13,15,12,12,11,11,10,8,9,10,12,12],
                        [8,8,7,9,6,6,7,6,5,5,6,3]]
        self.plant3_demand= [[40,48,40,35,33,27,38,38,32,26,45,42],
                        [6,6,7,5,7,5,6,5,6,7,6,4],
                        [15,15,15,13,11,15,12,9,9,11,11,10],
                        [7,8,8,8,7,6,8,8,6,8,5,5]]
        self.plant4_demand= [[50,55,45,45,40,32,35,42,30,32,47,40],
                        [6,6,6,5,4,7,7,7,9,8,7,7],
                        [12,12,13,12,11,15,8,9,10,11,11,12],
                        [7,8,7,6,6,9,8,7,7,7,7,6]]
        
        self.cost_of_workers=[4200,4800,5000,6600]
        
        self.cost_of_maintaining=[[35000,40000,41000],
                             [28000,30000,27000],
                             [25000,27000,28000],
                             [30000,35000,29000]]
        
        #Value of each 
        # i=workers, j=plant. k=month, c=candy type
        self.months = 12
        self.candys = 3
        self.plants = 4
        self.workers = 4
        
        
    def set_variables(self):
        self.assigned = []
        
        for _ in range(self.workers):
            worker_type_assignment = []
            for _ in range(self.plants):
                plant_assignment = []
                for _ in range(self.months):
                    plant_assignment.append(self.model.integer_var())
                worker_type_assignment.append(plant_assignment)
            self.assigned.append(worker_type_assignment)
            
        
        self.plant_produce_candy_y = []
        
        for _ in range(self.plants):
            plant_produce = []
            for _ in range(self.candys):
                plant_produce.append(self.model.binary_var())
            self.plant_produce_candy_y.append(plant_produce)
            
             
    def set_objective(self):
        
        total_worker_cost=sum(self.assigned[i][j][k]*self.cost_of_workers[i] 
                              for i in range(self.workers) 
                              for j in range(self.plants) 
                              for k in range(self.months))
        total_maintenance_cost=sum(self.plant_produce_candy_y[j][y] * self.cost_of_maintaining[j][y] 
                              for j in range(self.plants) 
                              for y in range(self.candys))
        self.model.minimize(total_worker_cost+total_maintenance_cost)
        
    def set_constraints(self): 
        #each candy has to be made at minimum 2 plants
        for y in range(self.candys):
            self.model.add_constraint(self.plant_produce_candy_y[0][y] +self.plant_produce_candy_y[1][y]
                                     + self.plant_produce_candy_y[2][y] +self.plant_produce_candy_y[3][y] >= 2)
        
        for k in range(self.months):
            for i in range(self.workers):
                for y in range(self.candys): 
                    self.model.add_constraint(self.plant1_demand[i][k]  <= self.assigned[i][0][k])
                    self.model.add_constraint(self.plant2_demand[i][k]  <= self.assigned[i][1][k])
                    self.model.add_constraint(self.plant3_demand[i][k]  <= self.assigned[i][2][k])
                    self.model.add_constraint(self.plant4_demand[i][k]  <= self.assigned[i][3][k])
        # 2 techs, 6 supers, 3 engineers for wwach candy at each plant constraints
        for j in range(self.plants):
            for k in range(self.months):
                self.model.add_constraint(self.assigned[1][j][k] >= 2* sum(self.plant_produce_candy_y[j][y] for y in range(self.candys)))
                self.model.add_constraint(self.assigned[2][j][k] >= 6* sum(self.plant_produce_candy_y[j][y] for y in range(self.candys)))
                self.model.add_constraint(self.assigned[3][j][k] >= 3* sum(self.plant_produce_candy_y[j][y] for y in range(self.candys)))
                
                
        #20% constraints
        for j in range(self.plants):
            for i in range(self.workers):
                for y in range(self.candys):
                    for k in range(1,12):
                        self.model.add_constraint(0.8 *self.assigned[i][j][k-1] <= self.assigned[i][j][k])
                        self.model.add_constraint(self.assigned[i][j][k] <= 1.2* self.assigned[i][j][k-1])

            
        # Candy FF can be made at plant 1 or plant 2 (NOT BOTH)
        self.model.add_constraint(self.plant_produce_candy_y[0][0] + self.plant_produce_candy_y[1][0] <= 1)
                   
        #IF CC is at platn 2, then must also at plant 4
        self.model.add_constraint(self.plant_produce_candy_y[1][1] <= self.plant_produce_candy_y[3][1])
        
        #TIS at either plant 1 or plant 4 (maybe both)
        self.model.add_constraint(self.plant_produce_candy_y[0][2] + self.plant_produce_candy_y[3][2] >= 1)


    def solve_model(self):
        solution=self.model.solve()
        
        if solution:
            print("                    Total Cost: $" + str(self.model.objective_value))
            print()
            print()
            j=0
            for workers in self.assigned:
                print(f"   {self.worker_job[j]}   ", end='')
                print()
                i=1
                for plants in workers:
                    print(f"            Plant{i}:            ", end="")
                    for month in plants:
                        print(int(month.solution_value),end=",")
                    print()
                    i+=1
                print()
                j+=1
                
            w=1
            
            
            print('Candy at Plants')
            print("        FF, CC, Tis")
            for plant in self.plant_produce_candy_y:
                print(f" Plant {w}:" , end="")
                y=0
                for candy in plant:
                    print(int(candy.solution_value), end ='   ')
                    y+=1
                print()
                w+=1
                
        else:
            print("Oopsies- No Solution Found")


# In[36]:


#Calling the Solver
solver = OR2_Integer_Project()
solver.set_variables()
solver.set_objective()
solver.set_constraints()
solver.solve_model()


# In[ ]:




