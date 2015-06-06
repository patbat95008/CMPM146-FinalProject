import json
from collections import namedtuple

import sys

import Queue
import heapq
from math import sqrt

with open('Crafting.json') as f:
	Crafting = json.load(f)
	
#print Crafting['Items']

#print Crafting['Initial']

#print Crafting['Goal']

#print Crafting['Recipes'].items

Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
t_limit = 20
Items = Crafting['Items']

#make_checker:
#Creates a function that takes the current state as an argument.
#The function uses the given rule to determine whether or not the current state applies or not.
#If all the items required by the rule are present within the state, the check function returns true. Otherwise, false.

#Arguments: rule. This is one of the recipes from Crafting.json.
#Returns: A function named check.

#check:
#Arguments: state. This is the current state.
#Returns: True if the state contains the items required by the rule, false otherwise.
def make_checker(rule):
	if 'Requires' in rule:
		requires = rule['Requires']
	else:
		requires = None
	if 'Consumes' in rule:
		consumes = rule['Consumes']
	else:
		consumes = None
	
	def check(state):
		for i,name in enumerate(Items):
			if requires != None and state.get(name, 0) < requires.get(name, 0):
				return False
			if consumes != None and state.get(name, 0) < consumes.get(name, 0):
				return False
		return True
	
	return check

#make_effector:
#Creates a function that takes the current state as an argument.
#The function uses the given rule to determine how it should modify the given state.
#The state should be changed by subtracting whatever is consumed by the rule, and adding whatever is created.

#Arguments: rule. This is one of the recipes from Crafting.json.
#Returns: A function named effect.

#effect:
#Arguments: state. The current state.
#Returns: A copy of the state (!) that has been modified by the rule given in make_effector.
def make_effector(rule):
	if 'Consumes' in rule:
		consumes = rule['Consumes']
	else:
		consumes = None
	produces = rule['Produces']
	def effect(state):
		state_copy = state.copy()
		if consumes != None:
			for i,name in enumerate(consumes):
				state_copy[name] -= consumes[name]
		for i,name in enumerate(produces):
			state_copy[name] += produces[name]
		return state_copy
	return effect

#make_initial_state:
#This basically creates a dictionary out of the given...dictionary?
#This function is probably redundant, but using it just in case, since this was in the base code.

#Arguments: inventory. This is an item from the Crafting dictionary. Used to make the initial_state
#using Crafting['Initial'], and the goal_state, using Crafting['Goal'].
#Returns: A dictionary of the given items for a current state. IE this state contains something like
#four planks, one bench, etc.
def make_initial_state(inventory):
	state = {}
	for i,name in enumerate(Items):
		state[name] = inventory.get(name, 0)
	return state

#The initial state of our machine is created here, using Crafting['Initial'].
initial_state = make_initial_state(Crafting['Initial'])

#make_goal_checker:
#Makes a function that determines whether or not the current state fulfils the goal.

#Arguments: goal. The dictionary for the goal, which is Crafting['Goal'] for Minecraft.
#Returns: a function named is_goal, which compares the values in Crafting['Goal'] and the given state.
#That function returns False if the goal conditions are not met, or true otherwise.
def make_goal_checker(goal):
	goal_state = make_initial_state(Crafting['Goal'])
	def is_goal(state):
		for i,name in enumerate(Items):
			#print("Item: " + str(name) + " Goal requirement: " + str(goal_state.get(name, 0)) + " State has: " + str(state.get(name, 0)))
			if goal_state.get(name, 0) > state.get(name, 0):
				return False
		return True
	return is_goal

goal_check = make_goal_checker(Crafting['Goal'])

#These two functions create representations of the current state, for the sake of hashing in dictionaries.
#inventory_to_tuple is not used, if I recall, but inventory_to_set is.

#inventory_to_set:
#Arguments: d, a given dictionary.
#Returns: A frozenset of the dictionary, allowing it to be used as a hash in another dictionary.
def inventory_to_tuple(d):
	return tuple(d.get(name,0) for i,name in enumerate(Items))

def inventory_to_set(d):
	return frozenset(d.items())
###
#heuristic:
#This is the function that is supposed to determine the distance to the goal, as per the A* algorithm.
#This function is probably where most of the remaining work needs to happen, although there is a possibility
#that more work might need to be done elsewhere.

#Arguments: state, the current state dictionary. You might want to add in the dictionary for the goal later on,
#which can be accessed in Crafting['Goal']?
#Returns: Currently, either 0 if the state is basically valid, or infinity if the inventory contains too many of one item (determined by the maximum of one item needed to make any other recipe.
#You may want to proofread the recipes possibly just in case I made a mistake?
#goal = {}
#initial_state = []
goal_state = make_initial_state(Crafting['Goal'])

def heuristic(state):
	#state_score = 0
   #Take the infinite if there are ever more items the necessary
	 if state["bench"] > 1 or state["cart"] > 1 or state["furnace"] > 1 or state["iron_axe"] > 1 or state["iron_pickaxe"] > 1 or state["stone_axe"] > 1 or state["stone_pickaxe"] > 1 or state["wooden_axe"] > 1 or state["wooden_pickaxe"] > 1:
          return sys.maxint


	 if state["coal"] > 1 and state["coal"] > goal_state["coal"]:
			 return sys.maxint
   
	 if state["cobble"] > 8 and state["cobble"] > goal_state["cobble"]:
			 return sys.maxint
   
	 if state["ingot"] > 6 and state["ingot"] > goal_state["ingot"]:
			 return sys.maxint
   
	 if state["ore"] > 1 and state["ore"] > goal_state["ore"]:
			 return sys.maxint
   
	 if state["plank"] > 4 and state["plank"] > goal_state["plank"]:
			 return sys.maxint
   
	 if state["stick"] > 4 and state["stick"] > goal_state["stick"]:
			 return sys.maxint
      
	 if state["wood"] > 1 and state["wood"] > goal_state["wood"]:
			 return sys.maxint
      
	 return 0

#This constructs the rules needed for the graph. This was given.
for name,rule in Crafting['Recipes'].items():
	checker = make_checker(rule)
	effector = make_effector(rule)
	recipe = Recipe(name, checker, effector, rule['Time'])
	all_recipes.append(recipe)

#The actual search algorithm itself.
#Arguments:
#graph: the function used to determine the valid edges for the current state.
#initial: The initial state.
#is_goal: The goal function used to determine if the algorithm is complete.
#limit: This is supposedly supposed to be used for the time limit, but it's not implemented yet.
#heuristic: The heuristic function.
def search(graph, initial, is_goal, limit, heuristic):
	#A* setup.
	frontier = Queue.PriorityQueue()
	#Again, when hashing for a dictionary, you need to call inventory_to_set on the state, otherwise
	#Python complains about a dictionary not being a hashable item (since it's mutuable?)
	#Whereas a frozenset isn't.
	initial_frozen = inventory_to_set(initial)
	frontier.put((0, initial))
	came_from = {}
	cost_so_far = {}
	came_from[initial_frozen] = None
	cost_so_far[initial_frozen] = 0
	current = []
	
	#This holds the name of each rule that is used, so that you can construct the list of instructions later.
	name_of = {}
	name_of[initial_frozen] = None
	
	visited = {}
	visited[initial_frozen] = True
	
	#This is pretty standard A*.
	while not frontier.empty():
		#print("New iteration state: ")
		pri,current = frontier.get()
		#print(current)
		current_frozen = inventory_to_set(current)
		#print("Cost so far: ")
		#print(cost_so_far)
		
		if is_goal(current):
			#print("Cake!")
			break
		
		for name,next_state,cost in graph(current):
			#print ("State name: " + str(name))
			#print ("Checking state: " + str(next_state))
			new_cost = cost_so_far[current_frozen] + cost
			#print ("New cost: " + str(new_cost))
			next_frozen = inventory_to_set(next_state)
			#print ("Old cost: " + str(cost_so_far.get(next_frozen, None)))
			if next_frozen not in cost_so_far or new_cost < cost_so_far[next_frozen]:
				#print("Adding!")
				visited[next_frozen] = True
				cost_so_far[next_frozen] = new_cost
				#print ("New cost: " + str(new_cost))
				priority = new_cost + heuristic(next_state)
				#print("Priority of next state: " + str(priority))
				frontier.put((priority, next_state))
				came_from[next_frozen] = current
				#print (next_state)
				#print ("Came from: ")
				#print (current)
				name_of[next_frozen] = name
	
	total_cost = cost_so_far[current_frozen]
	
	plan = []
	this_state = current
	#print(came_from)
	
	while this_state != None:
		#print(this_state)
		this_state_frozen = inventory_to_set(this_state)
		plan.append(name_of[this_state_frozen])
		this_state = came_from[this_state_frozen]
	
	plan.reverse()
	
	return total_cost, plan

#graph:
#Takes the current state, and returns every possible recipe to the search algorithm that can be used
#based on the available materials in the current state (in theory).
def graph(state):
	for r in all_recipes:
		if r.check(state):
			yield (r.name, r.effect(state), r.cost)

#This is basically the actual run of the program.
total_cost,plan = search(graph, initial_state, goal_check, t_limit, heuristic)
print ("Total cost: " + str(total_cost))
for i in range(1, len(plan)):
	print(plan[i])

