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


def push_summary_timeseries(data,a10a_info,column_names):   #push signals to amphora
    credentials = Credentials(username=a10a_info['username'], password=a10a_info['password'])
    client = AmphoraDataRepositoryClient(credentials)
    amphora = client.get_amphora(a10a_info['id'])   
    df = pd.DataFrame(data)
    df = df.rename(columns=column_names)
    new_df = df.drop(['day', 'day_fraction'], axis=1)
    Signal = new_df.to_dict('records')
    amphora.push_signals_dict_array(Signal)
    return

def push_snapshot(positions,status,current_time,a10a_info):         #push snapshot of data to amphora
    credentials = Credentials(username=a10a_info['username'], password=a10a_info['password'])
    client = AmphoraDataRepositoryClient(credentials)
    sep = '_'
    stor=[]
    for i in range(len(status)):
        stor.append([positions[i][0],positions[i][1],status[i]])
    #print(stor)
    filename = sep.join(["Positions_and_status_at_day",str(current_time),'for_run',str(a10a_info['run_id']),'.csv'])
    df = pd.DataFrame(np.array(stor))
    df.columns = ["position_x","position_y","health_status"]
    df.to_csv(filename)
    amphora = client.get_amphora(a10a_info['id']) 
    amphora.push_file(filename)
    os.remove(filename)
    return
    
    
def simulate_w_a10a(params, a10a_info, plt=None, plot_hourly=None, xlabel=None, callback=plot_callback , ad_upload = True):
    """ OU Pandemic simulation
    :param params:       dict of dict as per pandemic.conventions
    :param plt:          Handle to matplotlib plot
    :param plot_hourly:  Bool        Set False to speed up, True to see commuting
    :param xlabel:       str         Label for plot
    :param callback:     Any function taking home, work, day, params, positions, status (e.g. for plotting, saving etc)
    :return: None        Use the callback
    """

    if plot_hourly is None:
        plot_hourly = params['geometry']['n']<50000  # Hack, remove

    # Initialize a city's geography and its denizens
    num, num_initially_infected = int(params['geometry']['n']),int(params['geometry']['i'])
    num_times_of_day = int(params['motion']['t'])
    precision  = int(params['geometry']['p'])
    home, work = home_and_work_locations(geometry_params=params['geometry'],num=num)
    positions  = nudge(home,w=0.05*params['motion']['w'])
    status     = np.random.permutation([INFECTED]*num_initially_infected +[VULNERABLE]*(num-num_initially_infected))
    time_step  = 1.0/num_times_of_day

    # Population drifts to work and back, incurring viral load based on proximity to others who are infected
    day = 0
    while any( s in [ INFECTED ] for s in status ):

        day = day+1
        for step_no, day_fraction in enumerate(times_of_day(num_times_of_day)):
            stationary = [ s in [DECEASED, POSITIVE] for s in status ]
            attractors = destinations(status, day_fraction, home, work)
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=attractors,
                                          time_step=time_step , stationary=stationary )

            exposed = newly_exposed(positions=positions, status=status, precision=precision)
            current_time = day+day_fraction
            if abs(current_time % 1) <0.002:
                print(current_time)
                if ad_upload == True:
                    #print(positions+status)
                    push_snapshot(positions,status,current_time,a10a_info)
            status = contact_progression(status=status, health_params=params['health'], exposed=exposed)
            status = individual_progression(status, health_params=params['health'], day_fraction=time_step )
            if callback:
                callback(day=day, day_fraction=day_fraction , home=home, work=work, positions=positions, status=status, params=params, step_no=step_no, plot_hourly=plot_hourly, plt=plt)
    pprint(Counter([list(STATE_DESCRIPTIONS.values())[s] for s in status]))
    return data


def data_append(row: dict, key: str):
    if key in row:
        data[key].append(row[key])
    else:
        data[key].append(0)


# callback(day=day, day_fraction=day_fraction , home=home, work=work, positions=positions, status=status, params=params, step_no=step_no, plot_hourly=plot_hourly, plt=plt)
def c(day, day_fraction, home, work, positions, status, params, step_no, plot_hourly, plt ):
    t0 = datetime(2020, 4, 15, 3,30,0,0)
    unique, counts = np.unique(status, return_counts=True)
    d = dict(zip(unique, counts))
    # append things
    data['day'].append(day)
    data['day_fraction'].append(day_fraction)
    data['t'].append(t0 + timedelta(days=day, minutes=day_fraction * 3600))
    data_append(d, VULNERABLE)
    data_append(d, INFECTED)
    data_append(d, SYMPTOMATIC)
    data_append(d, POSITIVE)
    data_append(d, RECOVERED)
    data_append(d, DECEASED)
