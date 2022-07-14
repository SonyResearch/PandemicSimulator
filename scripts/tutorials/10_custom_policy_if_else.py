# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from tqdm import trange

import pandemic_simulator as ps
import random


def run_pandemic_gym_env() -> None:
    """Here we execute the gym envrionment wrapped simulator using austin regulations,
    a small town config and default person routines."""

    print('\nA tutorial that runs the OpenAI Gym environment wrapped simulator', flush=True)

    # init globals
    ps.init_globals(seed=104923490)

    # select a simulator config
    sim_config = ps.sh.small_town_config

    # make env

    wrap = ps.env.PandemicGymEnv3Act.from_config(sim_config = sim_config, pandemic_regulations=ps.sh.austin_regulations)

    # setup viz
    viz = ps.viz.GymViz.from_config(sim_config=sim_config)
    sim_viz = ps.viz.SimViz.from_config(sim_config=sim_config)

    # run stage-0 action steps in the environment
    wrap.env.reset()
    Reward = 0
    for i in trange(120, desc='Simulating day'):
        
        
        if i==0:
            action = 0 

        else:
            if i%10==0:
                viz.plot()
                sim_viz.plot()
                
#######################################################################################################################################            
#Replace the code in this if else statement with your own policy based on observation
            '''
            Access Infected flag (number of TESTED infected people >10): obs.infection_above_threshold[...,0]
            Access Stage: obs.stage[...,0]
            Access Day: obs.time_day[...,0]
            Access Not Infected Population(based on testing): obs.global_testing_state[...,3]
            Access Infected Population(based on testing): obs.global_testing_state[...,2]
            Access Critical Population(based on testing): obs.global_testing_state[...,0]
            Access Dead Population(based on testing): obs.global_testing_state[...,1]
            Access Recovered Population(based on testing): obs.global_testing_state[...,4]

            action = 1 increases current stage by 1
            action = 0 maintains current stage
            action = -1 decreases current stage by 1

            DO NOT ACCESS obs.global_infected_state as it doesnt reflect the real world scenario.
            '''
            if obs.time_day[...,0]>20:
                action = 1
            elif not obs.infection_above_threshold:
                action = 0
            else:
                action = -1

        obs, reward, done, aux = wrap.step(action=int(action))  # here the action is the discrete regulation stage identifier
        print(obs)
        Reward += reward
        viz.record((obs, reward))
        sim_viz.record_state(state = wrap.env.pandemic_sim.state)
########################################################################################################################################
    # generate plots
    viz.plot()
    sim_viz.plot()
    print('Reward:'+str(Reward))


if __name__ == '__main__':
    run_pandemic_gym_env()

