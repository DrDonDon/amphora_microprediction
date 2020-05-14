# -*- coding: utf-8 -*-
"""
Created on Mon May  4 09:49:22 2020

@author: Isaac Donnelly, Amphora Data
"""

# Import Amphora modules
from amphora.client import AmphoraDataRepositoryClient, Credentials

# Import Microprediction modules
from pandemic.plotting import plot_points, plot_callback
from pandemic.movement import nudge, times_of_day
from pandemic.city import home_and_work_locations
from pandemic.compliance import destinations
from pandemic.movement import evolve_positions, newly_exposed
from pandemic.health import contact_progression, individual_progression
from pandemic.conventions import VULNERABLE, INFECTED, SYMPTOMATIC, POSITIVE, RECOVERED, DECEASED, STATE_DESCRIPTIONS

# Import other modules
import pandas as pd
import os
import numpy as np
from pprint import  pprint
from collections import Counter
from datetime import datetime, timedelta

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

def create_amphora(params,param_name,username,password):    # Create new amphora for data
    credentials = Credentials(username=username, password=password)
    client = AmphoraDataRepositoryClient(credentials)    
    ## Create Amphora
    sep=" "
    amphora_description=sep.join(["Simulation of Pandemic code from Microprediction \n Parameter set is for",param_name," \n \
                                 N =",str(float(params['geometry']['n']))," \n I =",str(float(params['geometry']['i']))," \n \
                                 R =",str(float(params['geometry']['r']))," \n B =",str(float(params['geometry']['b']))," \n \
                                 H =",str(float(params['geometry']['h']))," \n C =",str(float(params['geometry']['c']))," \n \
                                 S =",str(float(params['geometry']['s']))," \n E =",str(float(params['geometry']['e']))," \n \
                                 P =",str(float(params['geometry']['p']))," \n T =",str(float(params['motion']['t']))," \n \
                                 K =",str(float(params['motion']['k']))," \n W =",str(float(params['motion']['w']))," \n \
                                 VI =",str(float(params['health']['vi']))," \n IS =",str(float(params['health']['is']))," \n \
                                 IP =",str(float(params['health']['ip']))," \n SP =",str(float(params['health']['sp']))," \n \
                                 IR =",str(float(params['health']['ir']))," \n ID =",str(float(params['health']['id']))," \n \
                                 SR =",str(float(params['health']['sr']))," \n SD =",str(float(params['health']['sd']))," \n \
                                 PD =",str(float(params['health']['pd']))," \n PR =",str(float(params['health']['pr']))])
    
    amphora_tnc="Creative_Commons_0"
    amphora_name=sep.join(["Ensemble simulation of Microprediction Pandemic for",param_name])
    labels=['Covid,simulation,timeseries',param_name]
    amphora = client.create_amphora(name = amphora_name, price = 0, description = amphora_description, terms_and_conditions_id = amphora_tnc, labels=labels)
    amphora_id = amphora.amphora_id
    
    # Create signals
    amphora.create_signal("vulnerable", attributes={"units":"#"})
    amphora.create_signal("infected", attributes={"units":"#"})
    amphora.create_signal("symptomatic", attributes={"units":"#"})
    amphora.create_signal("positive", attributes={"units":"#"})
    amphora.create_signal("recovered", attributes={"units":"#"})
    amphora.create_signal("deceased", attributes={"units":"#"})
    
    return amphora_id


def push_summary_timeseries(data,column_names, client, amphora_id):   #push signals to amphora
    amphora = client.get_amphora('amphora_id')   
    df = pd.DataFrame(data)
    df = df.rename(columns=column_names)
    new_df = df.drop(['day', 'day_fraction'], axis=1)
    Signal = new_df.to_dict('records')
    amphora.push_signals_dict_array(Signal)
    return

def push_snapshot(positions,status,current_time,client,amphora_id):         #push snapshot of data to amphora

    sep = '_'
    stor=[]
    for i in range(len(status)):
        stor.append([positions[i][0],positions[i][1],status[i]])
    #print(stor)
    filename = sep.join(["Positions_and_status_at_day",str(current_time),'for_run_104.csv'])
    df = pd.DataFrame(np.array(stor))
    df.columns = ["position_x","position_y","health_status"]
    df.to_csv(filename)
    amphora = client.get_amphora(amphora_id) 
    amphora.push_file(filename)
    os.remove(filename)
    return
    
    
def amphora_callback(day, day_fraction, home, work, positions, status, params, step_no, plot_hourly, plt):
    

    current_time = day + day_fraction
    if abs(current_time % 1) <0.002:
        # Login to amphoradata.com
        try:
            username=os.getenv('amphora_username')
            password=os.getenv('amphora_password')
            credentials = Credentials(username,password) 
            client = AmphoraDataRepositoryClient(credentials)
        except:
            print("Couldn't login. Please sign up at amphoradata.com/regsiter if you need a free account.")
                   
        # Check if amphora exists
        amphora_id = os.environ["amphora_id"]
        if amphora_id == None:
            param_name = "HOMESICK"
            amphora_id = create_amphora(params,param_name,username,password)
        
        # Push file (end of each day)
        print(current_time)
        push_snapshot(positions,status,current_time,client,amphora_id)
            
        # Push signal (when infected go to 0)
        if(sum(s in [ INFECTED ] for s in status )==0):
            push_summary_timeseries(data,column_names, client, amphora_id)
