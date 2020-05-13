# Amphora and microprediction

This repo is to demonstrate the benefits and methods for using Amphora and microprediction together. We have focused on the pandemic model 

Amphora is an invaluable data storage and collaboration tool. Any output from Microprediction can be stored and shared on Amphora in a very userfriendly and powerful manner. The output is viewable on [amphoradata.com](https://app.amphoradata.com/Amphorae/Detail?id=29ae56f6-cd0d-4e20-b6d2-9acf8fbf2495)

## Main code
The main code, [run.py](https://github.com/DrDonDon/amphora_microprediction/blob/master/run.py), runs a series of pandemic models. Daily data is pushed to amphoradata.com so any user can find and use data on all the agents in the model. 

## Supporting code
[amphoraMicroPrediction.py](https://github.com/DrDonDon/amphora_microprediction/blob/master/amphoraMicroPrediction.py) is a module for running run.py. It is tailored for pandemic atm but will be expanded to support MicroPrediction in general

[requirements.txt](https://github.com/DrDonDon/amphora_microprediction/blob/master/requirements.txt) is a list of all requirements to run this code.

[share_amphora.py](https://github.com/DrDonDon/amphora_microprediction/blob/master/share_amphora.py) is a simple file to share the Amphora with any user via their username/email address

## Three top uses of amphora with Microprediction
Microprediction users can use Amphora Data as an open source data collaboration tool

### Contribute your data to the community
Microprediction community members need a way to share data. They can test their models and showcase their prowess but can't store and share the data. Amphora lets them do this for free. Users can share their data with one-line commands or put it on the public repo for all to see

### Use someone elses model output
Any user of Amphora can get someone elses data on the platform. Many models are now open source but users typically need to run them themselves to get the data and insights, something which can be very computationally expensive. Instead, they can access the data instanly from Amphora.

### Use as a reference for article on linkedin etc
It is very easy to add a link to an Amphora for a reference in any article or github mention. Any reader can quickly access the data, in the same way they can access the code on github.


