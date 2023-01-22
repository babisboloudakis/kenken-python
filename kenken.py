# Imports
from csp import *
import time
import sys

# This KenKen model is based on
# https://github.com/aimacode/aima-python/blob/master


# PRE-BUILT KENKEN PUZZLES
# kenken puzzle format is a list where
# [ n, [var,var,...,var, goal, operation], ... [var,var,...,var, goal, operation] ]

# Easy kenken problem
veryeasy = [ 3, [ 0,1,3,'+' ], [ 2,5,5,'+'] , [3,3,'.'] , [4,6,7,6,'+'], [ 8,1,'.'] ]

# Easy kenken problem
easy = [ 3, [0,3,3,'+'], [1,2,1,'-'], [6,3,'.'], [4,7,2,'/'], [5,8,3,'/'] ]

# Medium kenken problem
medium = [4, [0,4,3,'-'], [1,5,2,'/'], [2,3,1,'-'], [6,7,4,'+'], [8,12,13,6,'*'], [9,10,14,8,'+'], [11,15,2,'/']  ]

# Hard kenken problem
hard = [ 6, [0,6,11,'+'], [1,2,2,'/'], [3,9,20,'*'], [4,5,11,17,6,'*'], [7,8,3,'-'], [10,16,3,'/'], [12,13,18,19,240,'*'], [14,15,6,'*'], [20,26,6,'*'], [21,27,28,7,'+'], [22,23,30,'*'], [24,25,6,'*'], [29,35,9,'+'], [30,31,32,8,'+'], [33,34,2,'/'] ]


# CSP class for KenKen problems
class Kenken(CSP):

    # Constructor for Kenken CSP problem
    def __init__(self, problem):
        
        # Initialize required data
        self.gridSize = problem[0]
        cells = self.gridSize*self.gridSize

        # Create a dictionary with
        # variable(key) - groupId(value)
        self.groups = {}
        self.groupsInfo = problem
        index = 1
        for i in problem[1:]:
            for j in i[:-2]:
                self.groups[j] = index
            index += 1

        # Create variable list
        # [0...NxN] where each variables number is col + row * N
        variables = [ i for i in range(cells) ]
        
        # Create a dictionary with domains for each variable
        VALUES = [ i+1 for i in range (self.gridSize) ]  # Possible values
        domains = {}
        for i in variables:
            domains[i] = VALUES
            if len(self.groupsInfo[self.groups[i]]) == 3:
                domains[i] = [ self.groupsInfo[self.groups[i]][-2] ]

        # Fill neughbours dictionary with the variables
        # in the same row, and in the same col
        self.neighbors = {}
        for i in variables:
            row = i // self.gridSize
            col = i % self.gridSize
            self.neighbors[i] = []
            # find neighboors for that variable
            for j in variables:
                row2 = j // self.gridSize
                col2 = j % self.gridSize
                if row == row2 and col == col2:
                    continue
                # if not the same variable
                if row == row2:
                    self.neighbors[i] += [j]
                elif col == col2:
                    self.neighbors[i] += [j]
        # Also add same group variables
        for i in variables:
            for j in self.groupsInfo[self.groups[i]][:-2]:
                if i == j: # Don't add yourself
                    continue
                self.neighbors[i] += [j]
            # Keep only unique values in neighbors list
            self.neighbors[i] = list(set(self.neighbors[i])) 

        # Initialize CSP problem
        CSP.__init__(self,variables,domains,self.neighbors,self.TestConstraints)


    # Funciton that returns true when two neighbours A and B
    # satisfy problem contraints for values a and b
    def TestConstraints(self, A, a, B, b):

        # As our variable are stored linearly we need
        # to extract their row and column
        rowA = A // self.gridSize
        colA = A % self.gridSize
        rowB = B // self.gridSize
        colB =  B % self.gridSize

        if rowA == rowB or colA == colB:
            # if same row or col, can't be same value
            if a == b:
                return False
        
        # now check for groups
        if self.groups[A] == self.groups[B]:
            # variables in the same group 
            # need to satisfy group constraints
            return self.GroupConstraints(A,a,B,b)
        
        return True


    # Test if a given group satisfies the problem constraints
    def GroupConstraints(self, A, a, B, b):

        # Initialize required data
        operator = self.groupsInfo[ self.groups[A] ][-1]
        goal = self.groupsInfo[ self.groups[A] ][-2]
        neighs = self.groupsInfo[ self.groups[A] ][:-2] # neighbours of A include B

        if operator == '+': # sum
            # True whenever the sum of a + b + rest = goal
            # Also true whenever a + b < goal when rest not calculated
            currentValues = self.infer_assignment()
            markedValues = 0
            for var in neighs:
                # we are counting marked values, B doesn't count
                if var in currentValues and var != B and var != A:
                    goal -= currentValues[var]
                    markedValues += 1
            if markedValues == ( len(neighs) - 2 ) : 
                # currently on last two values
                return a+b == goal
            elif markedValues < ( len(neighs) - 2 ) :
                # more variables to assign
                return a+b < goal
        elif operator == '*': # mult
            current = 1
            currentValues = self.infer_assignment()
            markedValues = 0
            for var in neighs:
                # we are counting marked values, B doesn't count
                if var in currentValues and var != B and var != A:
                    current = current * currentValues[var]
                    markedValues += 1
            if markedValues == (len(neighs) - 2) : 
                # all variables (in group ) assigned
                return a*b*current == goal
            elif markedValues < (len(neighs) - 2) :
                # there are more variables to assign
                return a*b*current <= goal
        elif operator == '-': # minus
            return abs(b-a) == goal
        elif operator == '/': # division
            # if either of the divisions is equal to the goal
            # return true
            return a/b == goal or b/a == goal
        # In any other case
        return False


    def display(self, assignment):
        # Function used to print a Kenken problem.
        # *** Used mostly for debugging purposes 
        print("Assignment is " + str(assignment) )
        values = assignment
        index = 0
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if index in values:
                    print("| "  + str(values[index]) , end=" ")
                else:
                    print("| "  + "_" , end=" ")
                index += 1
            print("| ")




# Solve Kenken puzzle using given algorithm 
# Print out execution time and total number of assignments
if len(sys.argv) < 2:
    print("Invalid arguments, please use")
    print("python3 kenken.py <algorithm> <puzzle>")
    sys.exit()

puzzle = sys.argv[2]
if puzzle == 'veryeasy':
    puzzle = veryeasy
elif puzzle == 'easy':
    puzzle = easy
elif puzzle == 'medium':
    puzzle = medium
elif puzzle == 'hard':
    puzzle = hard
else:
    print("Invalid puzzle, please use")
    print("easy, medium or hard")
    sys.exit()
alg = sys.argv[1]

if alg == 'BT':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = backtracking_search(kenken)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
elif alg == 'BT+MRV':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = backtracking_search(kenken, select_unassigned_variable=mrv)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
elif alg == 'FC':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = backtracking_search(kenken, inference=forward_checking)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
elif alg == 'FC+MRV':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = backtracking_search(kenken, select_unassigned_variable=mrv, inference=forward_checking)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
elif alg == 'MAC':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = backtracking_search(kenken, inference=mac)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
elif alg == 'MC':
    # Initialize puzzle
    kenken = Kenken(puzzle)
    # begin time
    beginTime = time.clock()
    # Execute selected algorithm
    assignment = min_conflicts(kenken)
    # Stop counting
    totalTime = time.clock() - beginTime
    # Print stats
    kenken.display(assignment)
    print("Execution time: " + str(totalTime ) )
    print("Total assignments: "  + str(kenken.nassigns) )
else:
    print("Invalid algorithm, please use")
    print("BT, BT+MRV, FC, FC+MRV, MAC or MC")
    sys.exit()