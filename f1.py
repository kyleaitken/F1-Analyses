### This script uses the data from fastf1 library to analyse Sergio Perez' controversial crash at the 
### end of qualifying at Monaco, 2022. We compare the throttle and braking data to visualize discrepencies 
### between his normal qualifying lap and the crash lap
###
### Credits to Jasper https://medium.com/@jaspervhat for the tutorials in utilizing the ff1 API

from xml.etree.ElementPath import get_parent_map
import pandas as pan
import fastf1 as ff1
import numpy as np

from fastf1 import plotting
import matplotlib.pyplot as pyp
from matplotlib.pyplot import figure

ff1.Cache.enable_cache('cache')

# Load session data for Sergio Perez, Monaco 2022 Qualifying
session = ff1.get_session(2022, 'Monaco', 'Q')
laps = session.load_laps(with_telemetry=True)
driver = 'PER'
driverLaps = laps.pick_driver(driver)

# Fastest Quali Lap
fastestLap = driverLaps.pick_fastest()
fastestLapData = fastestLap.get_car_data().add_distance()

# Last lap (Crash)
lastLap = driverLaps.loc[driverLaps['LapNumber'] == 25]
lastLapData = lastLap.get_car_data().add_distance()

# Get last corner data for last and fastest laps
lastCorner = lastLapData.loc[90:140]
lastCornerFastest = fastestLapData.loc[90:140]
cornerStartDistance = 1210
cornerEndDistance = 1390

# Label telem data into Braking, Accelerating, Cornering actions
lastCorner.loc[lastCorner['Brake'] > 0, 'CurrentAction'] = 'Braking'
lastCorner.loc[lastCorner['Throttle'] >= 80, 'CurrentAction'] = 'Throttle'
lastCorner.loc[(lastCorner['Brake'] == 0) & (lastCorner['Throttle'] < 80), 'CurrentAction'] = 'Cornering'

# Parse the different actions - cumsum takes the cumulative sum of the previous actions until it hits a new actionID
lastCorner['ActionID'] = (lastCorner['CurrentAction'] != lastCorner['CurrentAction'].shift(1)).cumsum()
driverActions = lastCorner[['ActionID', 'CurrentAction', 'Distance']].groupby(['ActionID', 'CurrentAction']).max('Distance').reset_index()
driverActions['DistanceDifference'] = driverActions['Distance'] - driverActions['Distance'].shift(1)
driverActions.loc[0, 'DistanceDifference'] = driverActions.loc[0, 'Distance']

# Average corner speed
avgSpeed = np.mean(lastCorner['Speed'].loc[(lastCorner['Distance'] >= cornerStartDistance) & (lastCorner['Distance'] <= cornerEndDistance)])

#Plot the Laps
pyp.rcParams["figure.figsize"] = [20, 20]

telemetryColors = {
    'Throttle': 'green', 
    'Cornering': 'blue',
    'Braking': 'red',
}

fig, ax = pyp.subplots(6)
fig.suptitle("Perez 2022 Monaco Crash Telemetry Analysis", fontsize = 40)


# Cornering Speed
ax[0].set_title("Cornering Speed & Brake/Throttle Points", fontsize = 25)
ax[0].plot(lastCorner['Distance'], lastCorner['Speed'], label=driver, color='black')

previousActionEnd = 0
for index, action in driverActions.iterrows():
    print(action)
    # make horizontal bar 
    ax[1].barh([driver], action['DistanceDifference'], left = previousActionEnd,
        color = telemetryColors[action['CurrentAction']]
    )
    previousActionEnd += action['DistanceDifference']


# Braking and Throttle Data
ax[2].set_title("Throttle - Crash/Last Lap", fontsize = 25)
ax[2].plot(lastCorner['Distance'], lastCorner['Throttle'])
ax[2].set_xlabel('Distance', fontsize=15)
ax[2].set_ylabel('Throttle', fontsize=20)

ax[3].set_title("Throttle - Fastest Lap", fontsize = 25)
ax[3].plot(lastCornerFastest['Distance'], lastCornerFastest['Throttle'])
ax[3].set_xlabel('Distance', fontsize=15)
ax[3].set_ylabel('Throttle', fontsize=20)

ax[4].set_title("Braking - Crash/Last Lap", fontsize = 25)
ax[4].plot(lastCorner['Distance'], lastCorner['Brake'])
ax[4].set_xlabel('Distance', fontsize=15)
ax[4].set_ylabel('Braking', fontsize=20)

ax[5].set_title("Braking - Fastest Lap", fontsize = 25)
ax[5].plot(lastCornerFastest['Distance'], lastCornerFastest['Brake'])
ax[5].set_xlabel('Distance', fontsize=15)
ax[5].set_ylabel('Braking', fontsize=20)


####
# Add style to plot
####

pyp.gca().invert_yaxis() # invert y axis

labels = list(telemetryColors.keys())
handles = [pyp.Rectangle((0,0),1,1, color=telemetryColors[label]) for label in labels]
ax[1].legend(handles,labels)

# Set x-axis bounds
for i in range(6):
    ax[i].set_xlim(cornerStartDistance, cornerEndDistance)

# Space between subplots
fig.subplots_adjust(hspace=.7)

ax[1].spines['top'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[1].spines['left'].set_visible(False)

pyp.savefig('2022_Monaco_Q_PER_Crash_Analysis')









 