from entities import Policy, Machine, MaintenanceTask, EpochResult
from engine import IndustrySim
from tools import e_greedy, NN
import numpy as np
import time
from industry import epoch_length, max_epochs, max_labor, wages, num_machines, job_demand
from industry import delay_penalty, mt_fixed_cost, mt_RF, mt_ttr, mt_labor, beta, age
from industry import compatible_jobs, machine_names, mt_task1, mt_task2, mt_task3
from industry import machine1, machine2, machine3

state_size = num_machines*2#+4
action_size = num_machines*3

start = time.time()
res = EpochResult(None, None, None)

nn = NN(dim_input=state_size, dim_hidden_layers=[10,10,10,10], dim_output=action_size, do_dropout=True, filename='delay_var.pickle')

states = np.zeros((max_epochs, state_size))
actions = np.zeros((max_epochs, action_size))
rewards = np.zeros(max_epochs)
state = np.zeros(state_size)

validation = 200
for delay_penalty in [0, 1, 5, 10, 25, 50, 100]:
	env = IndustrySim(machines=[machine1,machine2, machine3], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty, state_size=state_size)
	env.reset()
	print("Delay penalty: {}".format(delay_penalty))
	avg_obj = 0
	high_jobs = {
		'FnC1':0,
		'Lathe':0,
		'Milling':0
	}
	low_jobs = {
		'FnC1':0,
		'Lathe':0,
		'Milling':0
	}
	delay_cost = 0
	for exp in range(validation):
		for i in range(max_epochs):
			pm_probs = nn.run_forward(state, testing=True)
			pm_plan, action_vector = e_greedy(machine_names, pm_probs,e=None)
			#print(pm_plan)
			states[i] = state
			actions[i] = action_vector
			epoch_result, state = env.run_epoch(Policy('SJF', pm_plan))
		res = env.get_result()
		avg_obj += res.objfun
		for mr in res.machine_results:
			high_jobs[mr.name] += mr.mt_jobs_done['high']
			low_jobs[mr.name] += mr.mt_jobs_done['low']
			delay_cost += mr.delay_cost
		env.reset()
	avg_obj/=validation
	delay_cost/=validation
	delay_hours = 0
	if delay_penalty != 0:
		delay_hours = delay_cost/delay_penalty
	print('Avg obj: '+ str(avg_obj))
	print('Total high: '+str(high_jobs))
	print('Total low: '+ str(low_jobs))
	print('Delay: {} {}hrs'.format(delay_cost, delay_hours))
print('Took '+str(time.time()-start)+'s')