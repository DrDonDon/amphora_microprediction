# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:50:19 2020

@author: Isaac
"""

# Import modules
from amphora.client import AmphoraDataRepositoryClient, Credentials
import os

# Login to amphora
amphora_username=os.getenv('username')
amphora_password=os.getenv('password')
credentials = Credentials(username=amphora_username, password=amphora_password)
client = AmphoraDataRepositoryClient(credentials)

# Get amphora id
amphora_id = "29ae56f6-cd0d-4e20-b6d2-9acf8fbf2495"

# Share amphora
amphora = client.get_amphora(amphora_id)
amphora.share_with("isaacdonnelly@outlook.com")
