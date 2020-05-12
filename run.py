# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:23:54 2020

@author: Isaac
"""

from amphora.client import AmphoraDataRepositoryClient, Credentials
import amphoraMicroPrediction
from pandemic.example_parameters import TOY_TOWN
from pandemic.conventions import VULNERABLE, INFECTED, SYMPTOMATIC, POSITIVE, RECOVERED, DECEASED, STATE_DESCRIPTIONS


import numpy as np
import os

import time
import timeit
import mlflow
from datetime import datetime

## Set up log metrics
start = timeit.timeit()
sep='_'
mlflow.set_tracking_uri("http://aci-mlflow-dns.australiaeast.azurecontainer.io:5000/")
runName = sep.join(['Job_at',str(datetime.utcnow())])
mlflow.start_run(experiment_id=0, run_name =runName)
mlflow.log_metric("time_to_complete", 0)
mlflow.log_metric("ensembles_simulated",0)
mlflow.log_metric("run_complete",0)

N_S=30

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

# provide your login credentials

#amphora_id = amphoraMicroPrediction.create_amphora(params,param_set,amphora_username,amphora_password)
amphora_id = "29ae56f6-cd0d-4e20-b6d2-9acf8fbf2495"

                         
## Run pandemic and push to Amphora
for n_s in range(24, N_S):
    amphora_run_id = n_s
    print("Starting Simulation...")
    
    a10a_info = dict({'id': amphora_id,  'username': amphora_username, 'password': amphora_password, 'run_id': amphora_run_id})
    data = amphoraMicroPrediction.simulate_w_a10a(params, a10a_info, callback=amphoraMicroPrediction.c)
    amphoraMicroPrediction.push_summary_timeseries(data,a10a_info,column_names)
    
    print("Finished run")
    mlflow.log_metric("ensembles_simulated",n_s+1)
    time.sleep(5)
    
    
# Wrap up MLflow loggins    
end = timeit.timeit()
mlflow.log_metric("time_to_complete", end - start) 
mlflow.log_metric("run_complete",1)
mlflow.end_run() 
