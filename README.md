# PandemicSimulator

This repository implements a PandemicSimulator agent-based pandemic simulator. The main motivation behind the simulator is to model the effects of sequential decisions 
that can be made to manage the impact of COVID-19 virus and identify effective re-opening strategies.
The simulator comprises of multiple locations with different characteristics, different categories of people, 
and their realistic stateful behaviors that differ for each category. An OpenAI Gym environment is also made available to optimize a reopening strategy based on Reinforcement Learning.

See https://docs.google.com/document/d/16_LwPFMKI1Hqts6GeFZvqSJ2zKNzDWpemWUb8Oyrn_k for information on parameters used
in the model.

## Project Structure

`/docs` -- API documentation plus hierarchy 

`/python/pandemic_simulator/` -- Source files

`/scripts` -- Example scripts to run the simulator and the OpenAI gym environment

 
 ## Run the simulator
 To run the simulator, just execute the following in a bash (or equivalent) shell:
 
 `python3 scripts/run_pandemic_sim.py`
 
 The code runs the simulator under stage-0 policy (see http://austintexas.gov/covid19 for more info on stages). 
 
 Similarly, to run the OpenAI Gym env, execute the following:
 
 `python3 scripts/run_pandemic_env.py`
 
 ## Contact
 
 If you have any questions regarding the code, please feel free to contact
 Roberto Capobianco (roberto.capobianco@sony.com) or Varun Kompella (varun.kompella@sony.com).
 
 
###### Copyright 2020, Sony AI, Sony Corporation of America, All rights reserved.
 


