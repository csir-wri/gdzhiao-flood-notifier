# GDZHIAO Flood Forecasting System —  Flood Alerts Notifier

This Flood Alerts Notifier application receives data from the GDZHIAO Flood Forecasting System 
(GFFS) application and sends flood alerts to the recipients registered in the system.
The Flood Alerts Notifier application is designed to run on a fixed schedule, sending out the 
most recent updates received from the GFFS to the registered recipients via email and WhatsApp.


# Installation
## Windows
1. Download and install Python from https://www.python.org/downloads/windows/.  
   To be able to run the application safely ensure the minimum version downloaded is Python 3.10.

2. Download the ZIP source code of this repository [/archive/refs/heads/master.zip](/archive/refs/heads/master.zip)

3. Extract the ZIP to a location on your computer.

4. Run `setup.cmd` to set up the environment for running the script.


# Running the Application
## Windows
1. Enter the details of the alert recipients in the `/sample_data/recipients.csv` file.

2. Place the forecast CSV files obtained from the GFFS application in the `/sample_data/forecasts/` directory.

3. Run the `start.cmd` file to send the scheduled alerts.  
**NB:** You will be prompted to enter the credentials of the sending account if there are no saved credentials or the password has changed.


----------
 © 2025. Franz Alex GAISIE-ESSILFIE _(CSIR - Water Research Institute)_