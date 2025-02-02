# Critical Path Analysis 


# Problem description from Williams (2013, pages 95-98)
# Williams, H. Paul. 2013. Model Building in Mathematical Programming (fifth edition). New York: Wiley. [ISBN-13: 978-1-118-44333-0]

# Python PuLP solution prepared by Thomas W. Miller
# Revised April 20, 2023
# Implemented using activities dictionary with derived start_times and end_times
# rather than time decision variables as in Williams (2013)

from pulp import *

# Create a dictionary of the activities and their best case durations
activities_best_case = {'Describe_product':8, 'Marketing_strategy':24, 
              'Brochure':8, 'requirement_analysis':24, 
              'software_design':32, 'system_design':32, 
              'coding':128, 'documentation':32,
              'unit_test':48, 'system_test':24, 
              'package':24, 'market_survey':32,
              'pricing_plan':32, 'implementation_plan':16, 'client_proposal':16}


# Create a dictionary of the activities and their worst case durations
activities_worst_case = {'Describe_product':16, 'Marketing_strategy':32, 
              'Brochure':16, 'requirement_analysis':32, 
              'software_design':48, 'system_design':48, 
              'coding':160, 'documentation':48,
              'unit_test':64, 'system_test':32, 
              'package':36, 'market_survey':48,
              'pricing_plan':40, 'implementation_plan':24, 'client_proposal':24}

# Create a dictionary of the activities and their expected case durations
activities_expected_case = {'Describe_product':12, 'Marketing_strategy':28, 
              'Brochure':12, 'requirement_analysis':28, 
              'software_design':40, 'system_design':40, 
              'coding':144, 'documentation':40,
              'unit_test':56, 'system_test':28, 
              'package':30, 'market_survey':36,
              'pricing_plan':32, 'implementation_plan':20, 'client_proposal':20}

# Create a dictionary with hourly rates for each role
hourly_rates = {
    'project_manager': 61,
    'frontend_developer': 65,
    'backend_developer': 53,
    'data_scientist': 61,
    'data_engineer': 64,
    'UI_designer': 53,
    'QA_engineer': 47
}

# Assign out appropriate team members to each task
task_roles = {
    'Describe_product': ['project_manager'],
    'Marketing_strategy': ['project_manager'],
    'Brochure': ['UI_designer'],
    'requirement_analysis': ['project_manager', 'data_engineer'],
    'software_design': ['frontend_developer', 'backend_developer'],
    'system_design': ['frontend_developer', 'backend_developer'],
    'coding': ['backend_developer', 'data_scientist'],
    'documentation': ['project_manager', 'UI_designer'],
    'unit_test': ['QA_engineer'],
    'system_test': ['QA_engineer'],
    'package': ['project_manager', 'frontend_developer', 'backend_developer'],
    'market_survey': ['data_engineer'],
    'pricing_plan': ['project_manager', 'backend_developer'],
    'implementation_plan': ['project_manager', 'frontend_developer'],
    'client_proposal': ['project_manager']
}

# Create a dictionary of the activity precedences
precedences = {'Describe_product': [], 'Marketing_strategy': [], 'Brochure': ['Describe_product'], 
               'requirement_analysis': ['Describe_product'],'software_design': ['requirement_analysis'],
                'system_design': ['requirement_analysis'], 'coding': ['software_design','system_design'], 
               'documentation': ['coding'], 'unit_test': ['coding'],'system_test': ['unit_test'],
                 'package': ['documentation','system_test'], 'market_survey': ['Marketing_strategy','Brochure'],
                 'pricing_plan': ['package','market_survey'], 'implementation_plan': ['Describe_product','package'],
                 'client_proposal': ['pricing_plan','implementation_plan']}


# Create a list of the activities
activities_list = list(activities_best_case.keys())

# Create a dictionary of worker-task assignment variables
worker_assignment = {}
for activity in activities_list:
    for role in task_roles[activity]:
        worker_assignment[(activity, role)] = LpVariable(f"assigned_{activity}_{role}", 0, 1, LpBinary)

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list}

# Add the constraints
for activity in activities_list:
    prob += end_times[activity] == start_times[activity] + activities_best_case[activity], f"{activity}_duration"
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"

# Add constraint for worker assignment (a worker can work on only one task at a time)
    for role in task_roles[activity]:
        prob += lpSum(worker_assignment[(activity, role)]) == 1, f"worker_assignment_{activity}_{role}"


# Set the objective function
prob += lpSum([end_times[activity] for activity in activities_list]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for activity in activities_list:
    if value(start_times[activity]) == 0:
        print(f"{activity} starts at time 0")
    if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list]):
        print(f"{activity} ends at {value(end_times[activity])} hours in duration")

# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)


# Calculate total cost based on task roles and hourly rates for the best Case
total_cost = 0
for activity in activities_list:
    task_duration = activities_best_case[activity]  # Task duration for best case
    task_cost = 0
    num_roles = len(task_roles[activity])  # Number of roles assigned to the task
    hours_per_role = task_duration / num_roles  # Divide the task duration by the number of roles
    
    for role in task_roles[activity]:
        task_cost += hours_per_role * hourly_rates[role]  # Calculate cost for each role
    
    total_cost += task_cost
    print(f"Cost for {activity} ({task_duration} hours): ${task_cost:.2f}")
print("\nTotal project cost for best case scenario: ${:.2f}".format(total_cost))


### Replicating code for Worst Case Scenario (I'm sure there's a better way to do this but I was running out of time :| )

# Create a list of the activities
activities_list_worst = list(activities_worst_case.keys())

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list_worst}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list_worst}

# Add the constraints
for activity in activities_list_worst:
    prob += end_times[activity] == start_times[activity] + activities_worst_case[activity], f"{activity}_duration"
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"

# Add constraint for worker assignment (a worker can work on only one task at a time)
    for role in task_roles[activity]:
        prob += lpSum(worker_assignment[(activity, role)]) == 1, f"worker_assignment_{activity}_{role}"

# Set the objective function
prob += lpSum([end_times[activity] for activity in activities_list_worst]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for activity in activities_list_worst:
    if value(start_times[activity]) == 0:
        print(f"{activity} starts at time 0")
    if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list_worst]):
        print(f"{activity} ends at {value(end_times[activity])} hours in duration")

# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)


# Calculate total cost based on task roles and hourly rates for the worst Case
total_cost = 0
for activity in activities_list_worst:
    task_duration = activities_worst_case[activity]  # Task duration for worst case
    task_cost = 0
    num_roles = len(task_roles[activity])  # Number of roles assigned to the task
    hours_per_role = task_duration / num_roles  # Divide the task duration by the number of roles
    
    for role in task_roles[activity]:
        task_cost += hours_per_role * hourly_rates[role]  # Calculate cost for each role
    
    total_cost += task_cost
    print(f"Cost for {activity} ({task_duration} hours): ${task_cost:.2f}")
print("\nTotal project cost for worst case scenario: ${:.2f}".format(total_cost))


### Replicating code for Expected Case Scenario (I'm sure there's a better way to do this but I was running out of time :| )

# Create a list of the activities
activities_list_expected = list(activities_expected_case.keys())

# Create the LP problem
prob = LpProblem("Critical Path", LpMinimize)

# Create the LP variables
start_times = {activity: LpVariable(f"start_{activity}", 0, None) for activity in activities_list_expected}
end_times = {activity: LpVariable(f"end_{activity}", 0, None) for activity in activities_list_expected}

# Add the constraints
for activity in activities_list_expected:
    prob += end_times[activity] == start_times[activity] + activities_expected_case[activity], f"{activity}_duration"
    for predecessor in precedences[activity]:
        prob += start_times[activity] >= end_times[predecessor], f"{activity}_predecessor_{predecessor}"
# Add constraint for worker assignment (a worker can work on only one task at a time)
    for role in task_roles[activity]:
        prob += lpSum(worker_assignment[(activity, role)]) == 1, f"worker_assignment_{activity}_{role}"


# Set the objective function
prob += lpSum([end_times[activity] for activity in activities_list_expected]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Print the results
print("Critical Path time:")
for activity in activities_list_expected:
    if value(start_times[activity]) == 0:
        print(f"{activity} starts at time 0")
    if value(end_times[activity]) == max([value(end_times[activity]) for activity in activities_list_expected]):
        print(f"{activity} ends at {value(end_times[activity])} hours in duration")

# Print solution
print("\nSolution variable values:")
for var in prob.variables():
    if var.name != "_dummy":
        print(var.name, "=", var.varValue)



# Calculate total cost based on task roles and hourly rates for the Expected Case
total_cost = 0
for activity in activities_list_expected:
    task_duration = activities_expected_case[activity]  # Task duration for expected case
    task_cost = 0
    num_roles = len(task_roles[activity])  # Number of roles assigned to the task
    hours_per_role = task_duration / num_roles  # Divide the task duration by the number of roles
    
    for role in task_roles[activity]:
        task_cost += hours_per_role * hourly_rates[role]  # Calculate cost for each role
    
    total_cost += task_cost
    print(f"Cost for {activity} ({task_duration} hours): ${task_cost:.2f}")
print("\nTotal project cost for expected scenario: ${:.2f}".format(total_cost))
