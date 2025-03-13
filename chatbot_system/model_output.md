 ## Mathematical Model:
  To solve this problem, we need to construct a linear programming model to maximize the total profit while satisfying the constraints of the number of workers and machines. The model can be formulated as follows:

  ### Decision Variables:
  - \(x_1, x_2, x_3, x_4, x_5\): Represent the number of bolts, nuts, screws, gears, and bearings produced, respectively.

  ### Objective Function:
  - Maximize total profit: \(Z = 80x_1 + 90x_2 + 130x_3 + 50x_4 + 100x_5\)
  - This function calculates the total profit based on the number of bolts, nuts, screws, gears, and bearings produced and their respective profits.

  ### Constraints:
  1. Worker constraint: \(2x_1 + 3x_2 + 5x_3 + 1x_4 + 4x_5 \leq 200\)
  - This ensures that the total number of workers used does not exceed the available number of workers.
  2. Machine constraint: \(x_1 + 2x_2 + 3x_3 + 2x_4 + 4x_5 \leq 180\)
  - This ensures that the total number of machines used does not exceed the available number of machines.
  3. Production quantity constraints:
  - \(x_1 \geq 5\)
  - \(x_2 \geq 4\)
  - \(x_3 \geq 6\)
  - \(x_4 \geq 8\)
  - \(x_5 \geq 10\)
  - These constraints ensure that the production quantity of each component meets the minimum requirement.

  ### Non-negativity and Integer Constraints:
  - \(x_1, x_2, x_3, x_4, x_5 \geq 0\) and must be integers.

  Using this model, we can apply linear programming techniques to find the optimal production quantities of bolts, nuts, screws, gears, and bearings that maximize the total profit while satisfying the constraints of the number of workers and machines. This will provide the factory with an optimal production strategy to achieve maximum profit.

  ## Python Code Solution Using `discoptpy`:
  Below is a Python script using the `discoptpy` library to solve the problem:

  ```python
import coptpy as cp
from coptpy import COPT

# Create a COPT environment
env = cp.Envr()

# Create a COPT model
model = env.createModel("FactoryProductionOptimization")

# Add decision variables
x1 = model.addVar(vtype=COPT.INTEGER, name="x1") # Number of bolts
x2 = model.addVar(vtype=COPT.INTEGER, name="x2") # Number of nuts
x3 = model.addVar(vtype=COPT.INTEGER, name="x3") # Number of screws
x4 = model.addVar(vtype=COPT.INTEGER, name="x4") # Number of gears
x5 = model.addVar(vtype=COPT.INTEGER, name="x5") # Number of bearings

# Add constraints
model.addConstr(2*x1 + 3*x2 + 5*x3 + 1*x4 + 4*x5 <= 200, name="WorkerConstraint")
model.addConstr(x1 + 2*x2 + 3*x3 + 2*x4 + 4*x5 <= 180, name="MachineConstraint")
model.addConstr(x1 >= 5, name="BoltConstraint")
model.addConstr(x2 >= 4, name="NutConstraint")
model.addConstr(x3 >= 6, name="ScrewConstraint")
model.addConstr(x4 >= 8, name="GearConstraint")
model.addConstr(x5 >= 10, name="BearingConstraint")

# Set the objective function
model.setObjective(80*x1 + 90*x2 + 130*x3 + 50*x4 + 100*x5, sense=COPT.MAXIMIZE)

# Solve the model
model.solve()

# Analyze the solution
if model.status == COPT.OPTIMAL:
    print("Maximized total profit: {:.2f} yuan".format(model.objval))
    print("Optimal production quantities:")
    print("Bolts: {:.2f}".format(x1.x))
    print("Nuts: {:.2f}".format(x2.x))
    print("Screws: {:.2f}".format(x3.x))
    print("Gears: {:.2f}".format(x4.x))
    print("Bearings: {:.2f}".format(x5.x))
else:
    print("No optimal solution found.")
```

  This script first creates a COPT environment and model, then adds decision variables representing the number of bolts, nuts, screws, gears, and bearings produced. Next, it adds constraints to ensure that the total number of workers and machines used does not exceed the available number of workers and machines, and that the production quantity of each component meets the minimum requirement. Then, it sets the objective function to maximize the total profit. Finally, it solves the model and analyzes the solution. If an optimal solution is found, it prints the maximized total profit and the optimal production quantities of each component; otherwise, it prints a message indicating that no optimal solution was found. This script provides a complete solution to the problem using the