# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:23:54 2020

@author: Isaac
"""

# import amphora modules
from amphora.client import AmphoraDataRepositoryClient, Credentials
import amphoraMicroPrediction

# import microprediction modules
from pandemic.example_parameters import TOY_TOWN
from pandemic.conventions import VULNERABLE, INFECTED, SYMPTOMATIC, POSITIVE, RECOVERED, DECEASED, STATE_DESCRIPTIONS

# import generic modules
import numpy as np
import os
import time
import timeit
import mlflow
from datetime import datetime

# provide your login credentials
amphora_username = os.getenv('username')
amphora_password = os.getenv('password')

if not amphora_username:
    raise Exception("Amphora Username is required. Use an environment variable: username")
if not amphora_password:
    raise Exception("Amphora Password is required. Use an environment variable: password")

## Set up log metrics
start = timeit.timeit()
sep='_'
mlflow.set_tracking_uri("http://aci-mlflow-dns.australiaeast.azurecontainer.io:5000/")
runName = sep.join(['Job_at',str(datetime.utcnow())])
mlflow.start_run(experiment_id=0, run_name =runName)
mlflow.log_metric("time_to_complete", 0)
mlflow.log_metric("ensembles_simulated",0)
mlflow.log_metric("run_complete",0)

# Set number of runs
N_S=30

# Define variables
column_names = {
    't': 't',
    'day': 'day',
    'day_fraction': 'day_fraction',
    VULNERABLE: 'vulnerable',
    INFECTED: 'infected',
    SYMPTOMATIC: 'symptomatic',
    POSITIVE: 'positive',
    RECOVERED: 'recovered',
    DECEASED: 'deceased',
}

data = {
    't': [],
    'day': [],
    'day_fraction': [],
    VULNERABLE: [],
    INFECTED: [],
    SYMPTOMATIC: [],
    POSITIVE: [],
    RECOVERED: [],
    DECEASED: [],
}


# Choose parameter set
param_set = "TOY_TOWN"
params = TOY_TOWN
mlflow.log_param("run_type",param_set)
                  
## Run pandemic and push to Amphora
for n_s in range(N_S):
    
    amphora_run_id = n_s
    print("Starting Simulation...")
    print(n_s)
    
    data = simulate(params, callback=amphoraMicroPrediction.amphora_callback)
    
    print("Finished run")
    mlflow.log_metric("ensembles_simulated",n_s+1)
    
    
# Wrap up MLflow loggins    
end = timeit.timeit()
mlflow.log_metric("time_to_complete", end - start) 
mlflow.log_metric("run_complete",1)
mlflow.end_run() 
