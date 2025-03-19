# MAaD Science Video Extensometry using Computer Vision [Revised: July 2022]

# Imported libraries
import os
import sys
import cv2
import win32gui
import win32con
import tkinter as tk
import tkinter.ttk as ttk
from Settings import *
from csv import writer
from time import sleep
from queue import Queue
from pandas import read_csv
from threading import Thread
from datetime import datetime
from pykeyboard import PyKeyboard
from itertools import zip_longest
from os import system, execl, path
from tkinter import filedialog as fd
from scipy.interpolate import interp1d
from tkinter.scrolledtext import ScrolledText
from statsmodels.nonparametric.smoothers_lowess import lowess

# Define the welcome greeting
def welcome():
    clear = lambda: system('cls')
    clear()

    print('--MAaD Extensometry--')
    print('Video Extensometry using Computer Vision')
    print('Version 1.0, July 1st 2022')
    print('\nNOTES')
    print(' - When updating values in the entry boxes press enter to confirm')
    print(' - App limited to extension in the horizontal direction only')
    print(' - Select Help (File -> Help) for details on running extensometry or strain-to-stress correlation')
    print(' - Refer to the Messages window for details during analysis')
    print(' - Default settings can be updated in Settings.py or by saving settings')
    print('\nQUICK START')
    print(' - Press Select Video and then press Start')

# Define the about button
def info():
    if True:
        print('\nABOUT')
        print(' - This app is based upon OpenCV (https://opencv.org/)')
        print(' - Contact Mychal Spencer (mychal.spencer@pnnl.gov) or Donghui Li (donghui.li@pnnl.gov) with questions')

# Define the help button
def help():
    if True:
        help_extensometry()
        help_stress()

# Define extensometry help
def help_extensometry():
    if True:
        print('\nEXTENSOMETRY ANALYSIS')
        print('- Estimate material elongation using computer vision')
        print('    * Requires video with object (e.g., dogbone) extended in the horizontal direction only')
        print('    * Improve resolution by increasing video resolution or increasing size of object in frame')
        print('    * Tracker color turns red when tracking has been lost')
        print('    * Failure assumed when tracker lost or break point achieved (see Options -> Settings)')
        print('1. Update tracker type (additional settings: Options -> Settings)')
        print('2. Select a single video using the Select Video button')
        print('3. Press Start to start extensometry analysis')
        print('4. Draw a box around the first gauge mark (ensure center line is lined up with gauge mark)')
        print('5. Press Lock Tracker 1')
        print('6. Draw a box around the second gauge mark')
        print('7. Press Lock Tracker 2')
        print('8. Output csv is stored in the root directory')

# Define stress help
def help_stress():
    if True:
        print('\nSTRAIN-TO-STRESS CORRELATION')
        print('- Correlate video extensometry strain to measured load frame stress')
        print('    * Requires both time (s) and stress data from load frame')
        print('    * For strain, input file is output csv from extensometry analysis')
        print('    * For stress, input file is csv with form indicated by Stress File Indices (Options -> Settings)')
        print('    * Requires smoothing (LOWESS) of input data controlled via fractions (Options -> Settings)')
        print('    * Important: Assumes end data point for stress and strain is equivalent (e.g., at break)')
        print('    * Important: Assumes no repeating data points for stress')
        print('1. Update correlation settings (Options -> Settings)')
        print('2. Start strain-to-stress correlation (Options -> Strain-to-Stress)')
        print('3. Select stress input file with indicated form')
        print('4. Select strain input file')
        print('5. Output csv is stored in the root directory')

# Define the break point help button
def help_bp():
    if True:
        print('\nBREAK POINT')
        print(' - Integer value only')
        print(' - Represents the frame-to-frame extension in pixels beyond which the object has failed')
        print(' - The extensometry app stops collecting data once the break point has been reached')
        print(' - Set this value high (e.g., 1000) to analyze entire videos')
        print(' - Enable auto break point detection to automatically stop processing if tracker object is lost')
        print('    * Can only be enabled or disabled within Settings.py (1 = on, 0 = off)')

# Define the frame skipping help button
def help_skipping():
    if True:
        print('\nFRAME SKIPPING')
        print(' - Currently disabled')
        print(' - Represents number of frames to skip during processing (0 = none, 1 = 1 out of 2, 2 = 2 out of 3, etc.)')
        print(' - High values of frame skipping can lead to erroneous extensometry results')

# Define the strain fraction help button
def help_frac_strain():
    if True:
        print('\nLOWESS FILTERING FRACTION (STRAIN)')
        print(' - Between 0 and 1, representes the size of the LOWESS smoothing window')
        print(' - Default value of 0 uses a filter size of 40 data points for strain')

# Define the stress fraction help button
def help_frac_stress():
    if True:
        print('\nLOWESS FILTERING FRACTION (STRESS)')
        print(' - Between 0 and 1, representes the size of the LOWESS smoothing window')
        print(' - Default value of 0 uses a filter size of 10 data points for stress')

# Define the secant help button
def help_secant():
    if True:
        print('\nSECANT MODULUS')
        print(' - Integer value only')
        print(' - Evaluated strain (%) for secant calculation')
        print(' - If evaluated secant strain is beyond maximum strain, value will not be calculated')

# Define the file type help button
def help_file_type():
    if True:
        print('\nSTRESS FILE INDICES')
        print(' - Integer value only')
        print(' - Represents the start location index of stress data in imported stress csv')
        print(' - It is assumed that the first row always contains header information, not data')
        print(' - For rows: point to location of header data (one row only)')
        print(' - For columns: point to location of data')
        print(' - Format: [Time (s) Row] [Time (s) Column] [Stress Row] [Stress Column]')
        print(' - General: [1] [1] [1] [2] for csv of format Time (s) | Stress')
        print(' - Instron: [16] [1] [16] [3] for header on 16th row, and Time (s) in 1st and Stress in 3rd column')

# Define tracker help button
def help_tracker():
    if True:
        print('\nTRACKER TYPE')
        print(' - The tracker types are various algorithms used to establish the identity of objects across frames')
        print(' - Default tracker type of CSRT for high extension materials (e.g., polymers)')
        print(' - More details can be found at: https://docs.opencv.org/3.4/d9/df8/group__tracking.html')

# Define the reset button
def rerun():
    if True:
        sys.stdout.flush()
        python = sys.executable
        execl(python, python, * sys.argv)

# Define the quit button
def stop():
    if True:
        sys.exit()

# Define the stress correlation button
def stress():

    # Pull in data from the GUI
    parameters_Correlation() # Ensure only one item in queues and replace items

    frac_stress = float(shr_frac_stress.get()) # Fraction stress
    shr_frac_stress.put(frac_stress)
    frac_strain = float(shr_frac_strain.get()) # Fraction strain
    shr_frac_strain.put(frac_strain)
    input_secant1 = int(shr_secant1.get()) # Secant 1
    shr_secant1.put(input_secant1)
    input_secant2 = int(shr_secant2.get()) # Secant 2
    shr_secant2.put(input_secant2)
    input_secant3 = int(shr_secant3.get()) # Secant 3
    shr_secant3.put(input_secant3)
    input_secant4 = int(shr_secant4.get()) # Secant 4
    shr_secant4.put(input_secant4)
    input_stress_row = int(shr_stress_row.get())-1 # Stress row
    shr_stress_row.put(input_stress_row+1)
    input_stress_column = int(shr_stress_column.get())-1 # Stress column
    shr_stress_column.put(input_stress_column+1)
    input_time_row = int(shr_time_row.get())-1 # Time row
    shr_time_row.put(input_time_row+1)
    input_time_column = int(shr_time_column.get())-1 # Time column
    shr_time_column.put(input_time_column+1)
    
    Secant = [input_secant1, input_secant2, input_secant3, input_secant4] # Evaluated secant modulus in percent
    
    if frac_stress < 0 or frac_stress > 1:
        print('\nERROR: LOWESS fraction for stress must be between 0 and 1')
        return

    if frac_strain < 0 or frac_strain > 1:
        print('\nERROR: LOWESS fraction for strain must be between 0 and 1')
        return

    # Import stress and strain csv files and initialize lists
    video_Path_Stress = fd.askopenfilename(title='Select tensile frame output csv with indicated form')
    video_Path_Strain = fd.askopenfilename(title='Select video extensometry output csv in form: Time (s) | Gauge Length (Pixels)')

    Stress_Name = path.splitext(video_Path_Stress)[0]
    Stress_Name = path.split(Stress_Name)[1]

    try:
        stress_File = read_csv(video_Path_Stress,skip_blank_lines=False) # Imported stress file

    except IOError:
        print('\nERROR: No stress file selected')
        return

    try:
        strain_File = read_csv(video_Path_Strain,skip_blank_lines=False) # Imported strain file, assumed to be of the format: Time (s) | Pixel Displacement

    except IOError:
        print('\nERROR: No strain file selected')
        return

    try:
        data_Stress = stress_File.iloc[:,input_stress_column]

    except IndexError:
        print('\nERROR: Stress indices are incorrect, update correlation settings (Options -> Settings)')
        return

    data_Stress = data_Stress.iloc[input_stress_row:]

    try:
        data_Stress_Time = stress_File.iloc[:,input_time_column]

    except IndexError:
        print('\nERROR: Stress indices are incorrect, update correlation settings (Options -> Settings)')
        return

    data_Stress_Time = data_Stress_Time.iloc[input_time_row:]
    
    data_Strain = strain_File.iloc[:,1]
    data_Strain_Time = strain_File.iloc[:,0]

    output_Stress = list()
    output_Strain = list()
    output_Strain_Percent = list()

    output_Strain.append('Pixel Displacement (a.u.)')
    output_Stress.append('Stress')
    output_Strain_Percent.append('Strain (%)')

    # Convert to numpy data type
    data_Stress = data_Stress.to_numpy()
    
    try:
        data_Stress = data_Stress.astype(float)
    
    except ValueError:
        print('\nERROR: Stress indices are incorrect, update correlation settings (Options -> Settings)')
        return
    
    data_Stress_Time = data_Stress_Time.to_numpy()
    
    try:
        data_Stress_Time = data_Stress_Time.astype(float)
    
    except ValueError:
        print('\nERROR: Stress indices are incorrect, update correlation settings (Options -> Settings)')
        return

    data_Strain = data_Strain.to_numpy()
    data_Strain_Time = data_Strain_Time.to_numpy()

    # Calculate the tensile strength and max times
    TS = data_Stress.max()
    max_Stress_Time = data_Stress_Time.max()
    max_Strain_Time = data_Strain_Time.max()

    # Determine if strain or stress has a shorter time length (delta) and shift by delta
    if max_Stress_Time > max_Strain_Time:
        time_Delta = max_Stress_Time - max_Strain_Time
        time_Delta_Index = 1
        data_Strain_Time = data_Strain_Time + time_Delta

    else:
        time_Delta = max_Strain_Time - max_Stress_Time
        time_Delta_Index = 0
        data_Stress_Time = data_Stress_Time + time_Delta
    
    # Determine optimal LOWESS filter fraction based upon size of data (average 15 data points)
    if frac_stress == 0:
        frac_stress = 10/len(data_Stress)

    if frac_strain == 0:
        frac_strain = 40/len(data_Strain)
    
    # Apply LOWESS filtering to the input data (necessary for correlation)
    filtered_Stress = lowess(endog=data_Stress,exog=data_Stress_Time,frac=frac_stress,is_sorted=True)
    filtered_Strain = lowess(endog=data_Strain,exog=data_Strain_Time,frac=frac_strain,is_sorted=True)

    data_Stress = filtered_Stress[:,1]
    data_Stress_Time = filtered_Stress[:,0]
    data_Strain = filtered_Strain[:,1]
    data_Strain_Time = filtered_Strain[:,0]

    # Fit the stress data based upon time and then correlate to strain
    fit_Stress = interp1d(data_Stress_Time,data_Stress,kind='linear',axis=0)
    
    j = 0
    
    if time_Delta_Index == 0:

        for i in data_Strain_Time: # If strain has the longer time series

            if i >= time_Delta:
                output_Strain.append(data_Strain[j])
                output_Stress.append(fit_Stress(data_Strain_Time[j]))

            j = j + 1

    else:
    
        for i in data_Stress_Time: # If stress has the longer time series

            if i >= time_Delta:
                output_Strain.append(data_Strain[j])
                output_Stress.append(fit_Stress(data_Strain_Time[j]))

            j = j + 1

    output_Stress[1] = 0 # Initialize stress at 0
    orig_Gauge = output_Strain[1] # Initial gauge length at start time

    # Calculate the strain based upon the identified start time
    for i in output_Strain[1:]:
        output_Strain_Percent.append(100*(i-orig_Gauge)/orig_Gauge)

    # Calculate the elongation at break
    EAB = output_Strain_Percent[len(output_Strain_Percent)-1]

    # Confirm secant modulus locations are within elongation at break
    j = len(Secant)

    while j >= 0:
    
        if Secant[j-1] > EAB:
            Secant = Secant[:-1] # Remove secant locations outside EAB

        j = j - 1

    j = 1
    a = 0
    b = 0
    c = 0
    d = 0

    # Calculate the secant modulus
    for i in output_Strain_Percent[1:]:
    
        if len(Secant) >= 1:
        
            if i >= Secant[0] and a == 0:
                Secant1 = 100*output_Stress[j]/Secant[0]
                a = 1  

        if len(Secant) >= 2:
        
            if i >= Secant[1] and b == 0:
                Secant2 = 100*output_Stress[j]/Secant[1]
                b = 1

        if len(Secant) >= 3:
        
            if i >= Secant[2] and c == 0:
                Secant3 = 100*output_Stress[j]/Secant[2]
                c = 1

        if len(Secant) >= 4:
        
            if i >= Secant[3] and d == 0:
                Secant4 = 100*output_Stress[j]/Secant[3]
                d = 1

        j = j + 1

    # Append data for output
    info = list()
    info_data = list()
    
    j = 0

    while j < 7:
    
        if j == 0:
            info.append('File Name')
            info_data.append(Stress_Name)
        
        if j == 1:
            info.append('Elongation at Break (%)')
            info_data.append(EAB)
        
        if j == 2:
            info.append('Tensile Strength')
            info_data.append(TS)
        
        if j == 3:
            if len(Secant) >= 1:
                info.append(str(Secant[0]) + '% Secant Modulus')
                info_data.append(Secant1)
        
        if j == 4:
            if len(Secant) >= 2:
                info.append(str(Secant[1]) + '% Secant Modulus')
                info_data.append(Secant2)
            
        if j == 5:
            if len(Secant) >= 3:
                info.append(str(Secant[2]) + '% Secant Modulus')
                info_data.append(Secant3)
        
        if j == 6:
            if len(Secant) >= 4:
                info.append(str(Secant[3]) + '% Secant Modulus')
                info_data.append(Secant4)

        j = j + 1

    # Output the correlated stress and strain
    current_Date = str(datetime.now())
    current_Date = current_Date[2:4:1] + current_Date[5:7:1] + current_Date[8:10:1]
    Stress_Strain = Stress_Name + "_Correlated_" + current_Date + ".csv"

    with open(Stress_Strain, "w") as f:
        writer_Out = writer(f, lineterminator = '\n')

        for i in (tuple(p for p in pair if p is not None) for pair in 
                zip_longest(output_Strain_Percent, output_Stress, output_Strain, info, info_data)):
            writer_Out.writerow(i)

    # Indicate analysis completed successfully
    print('\nCOMPLETED strain-to-stress correlation:')
    print(' - LOWESS fraction for stress of ' + str(frac_stress))
    print(' - LOWESS fraction for strain of ' + str(frac_strain))
    print(' - Secant modulus of ' + str(Secant) + '%')
    print(' - Stress file indices of [' + str(input_time_row+1) + '] [' + str(input_time_column+1) + '] [' + str(input_stress_row+1) +  '] ['  + str(input_stress_column+1) + ']')

# Define file selection
def getPath():
    if True:
        videoPath = fd.askopenfilename(title='Select file for video extensometry analysis')
        print('\nThe video path has been updated to ' + videoPath)
        shr_path.put(videoPath)

# Update datasharing to ensure that only the last queue value is present when called
def parameters():
    if Queue.qsize(shr_bp) > 1:
    
        for i in range(Queue.qsize(shr_bp)-1):
            remov = shr_bp.get()

    if Queue.qsize(shr_skip) > 1:

        for i in range(Queue.qsize(shr_skip)-1):
            remov = shr_skip.get()

    if Queue.qsize(shr_path) > 1:
    
        for i in range(Queue.qsize(shr_path)-1):
            remov = shr_path.get()

    elif Queue.qsize(shr_path) == 0:
        print('\nFile location must be indicated')
        sleep(2)
        sys.exit()

    if Queue.qsize(shr_tracker) > 1:

        for i in range(Queue.qsize(shr_tracker)-1):
            remov = shr_tracker.get()

# Update datasharing for correlation
def parameters_Correlation():
    if Queue.qsize(shr_frac_strain) > 1:
    
        for i in range(Queue.qsize(shr_frac_strain)-1):
            remov = shr_frac_strain.get()
    
    if Queue.qsize(shr_frac_stress) > 1:
    
        for i in range(Queue.qsize(shr_frac_stress)-1):
            remov = shr_frac_stress.get()

    if Queue.qsize(shr_secant1) > 1:
    
        for i in range(Queue.qsize(shr_secant1)-1):
            remov = shr_secant1.get()
    
    if Queue.qsize(shr_secant2) > 1:
    
        for i in range(Queue.qsize(shr_secant2)-1):
            remov = shr_secant2.get()    
    
    if Queue.qsize(shr_secant3) > 1:
    
        for i in range(Queue.qsize(shr_secant3)-1):
            remov = shr_secant3.get()   

    if Queue.qsize(shr_secant4) > 1:
    
        for i in range(Queue.qsize(shr_secant4)-1):
            remov = shr_secant4.get()

    if Queue.qsize(shr_stress_row) > 1:

        for i in range(Queue.qsize(shr_stress_row)-1):
            remov = shr_stress_row.get()

    if Queue.qsize(shr_stress_column) > 1:

        for i in range(Queue.qsize(shr_stress_column)-1):
            remov = shr_stress_column.get()    

    if Queue.qsize(shr_time_row) > 1:

        for i in range(Queue.qsize(shr_time_row)-1):
            remov = shr_time_row.get()   

    if Queue.qsize(shr_time_column) > 1:

        for i in range(Queue.qsize(shr_time_column)-1):
            remov = shr_time_column.get()

# Mimic tracker lock buttons as key presses
def tracker_Lock(index):

    # Find the inactive extensometry window to send the key commands to
    hwndMain = win32gui.FindWindow(None, "MAaD Extensometry at PNNL")
    hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)
    win32gui.SetForegroundWindow(hwndChild) 

    # Tracker 1
    if index == 0:
        k = PyKeyboard()
        k.tap_key(0xff0d)
        sleep(0.05)
        k.tap_key(' ')

    # Tracker 2
    if index == 1:
        k = PyKeyboard()
        k.tap_key(0xff0d)
        sleep(0.05)
        k.tap_key('q')

# Define saving settings
def save_Settings():

    parameters() # Ensure only one item in queues and replace items
    parameters_Correlation()

    trackerType = shr_tracker.get() # Tracker type
    shr_tracker.put(trackerType)
    bp = int(shr_bp.get()) # Break point
    shr_bp.put(bp)
    skip = int(shr_skip.get()) # Frame skipping
    shr_skip.put(skip)
    frac_strain = float(shr_frac_strain.get()) # Fraction strain
    shr_frac_strain.put(frac_strain)
    frac_stress = float(shr_frac_stress.get()) # Fraction stress
    shr_frac_stress.put(frac_stress)
    input_secant1 = int(shr_secant1.get()) # Secant 1
    shr_secant1.put(input_secant1)
    input_secant2 = int(shr_secant2.get()) # Secant 2
    shr_secant2.put(input_secant2)
    input_secant3 = int(shr_secant3.get()) # Secant 3
    shr_secant3.put(input_secant3)
    input_secant4 = int(shr_secant4.get()) # Secant 4
    shr_secant4.put(input_secant4)
    input_stress_row = int(shr_stress_row.get()) # Stress row
    shr_stress_row.put(input_stress_row)
    input_stress_column = int(shr_stress_column.get()) # Stress column
    shr_stress_column.put(input_stress_column)
    input_time_row = int(shr_time_row.get()) # Time row
    shr_time_row.put(input_time_row)
    input_time_column = int(shr_time_column.get()) # Time column
    shr_time_column.put(input_time_column)

    settings_Output = list()
    
    settings_Output.append("tracker='"+str(trackerType)+"'")
    settings_Output.append('bp='+str(bp))
    settings_Output.append('auto_bp='+str(auto_bp))
    settings_Output.append('skip='+str(skip))
    settings_Output.append('frac_strain='+str(frac_strain))
    settings_Output.append('frac_stress='+str(frac_stress))
    settings_Output.append('secant1='+str(input_secant1))
    settings_Output.append('secant2='+str(input_secant2))
    settings_Output.append('secant3='+str(input_secant3))
    settings_Output.append('secant4='+str(input_secant4))
    settings_Output.append('stress_row='+str(input_stress_row))
    settings_Output.append('stress_column='+str(input_stress_column))
    settings_Output.append('time_row='+str(input_time_row))
    settings_Output.append('time_column='+str(input_time_column))

    # Save updated settings to Settings.py
    with open('Settings.py', "w") as f:
        writer_Out = writer(f, lineterminator = '\n')
        
        for row in settings_Output:
            writer_Out.writerow([row])

    print('\nSettings file has been updated')

# Define the console ouput to textbox
class PrintLogger(object):

    def __init__(self, textbox):  
        self.textbox = textbox # Pass reference to text widget

    def write(self, text):
        self.textbox.configure(state='normal')  # Make field editable
        self.textbox.insert('end', text)  # Write text to textbox
        self.textbox.see('end')  # Scroll to end
        self.textbox.configure(state='disabled')  # Make field read only

    def flush(self):
        pass

# Define the GUI
class App():

    #def callback(self):
        #root.quit() # Close program when root window is closed

    def closing(self):
        quit() # Close program when main window is closed

    def enter_bp(self, event):
        print('\nThe break point has been updated to ' + event.widget.get() + ' pixels')
        shr_bp.put(event.widget.get()) # Store user input values based upon enter key

        if Queue.qsize(shr_bp) > 1:

            for i in range(Queue.qsize(shr_bp)-1):
                remov = shr_bp.get()

    def enter_skip(self, event):
        print('\nFrame skipping has been updated to ' + event.widget.get() + ' frame(s)')
        shr_skip.put(event.widget.get()) # Store user input values based upon enter key
        
        if Queue.qsize(shr_skip) > 1:
    
            for i in range(Queue.qsize(shr_skip)-1):
                remov = shr_skip.get()

    def enter_frac_stress(self, event):
        print('\nThe filtering fraction for stress has been updated to ' + event.widget.get())
        shr_frac_stress.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_frac_stress) > 1:
    
            for i in range(Queue.qsize(shr_frac_stress)-1):
                remov = shr_frac_stress.get()

    def enter_frac_strain(self, event):
        print('\nThe filtering fraction for strain has been updated to ' + event.widget.get())
        shr_frac_strain.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_frac_strain) > 1:
    
            for i in range(Queue.qsize(shr_frac_strain)-1):
                remov = shr_frac_strain.get()

    def enter_secant1(self, event):
        print('\nThe first secant modulus has been updated to ' + event.widget.get() + '%')
        shr_secant1.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_secant1) > 1:
    
            for i in range(Queue.qsize(shr_secant1)-1):
                remov = shr_secant1.get()

    def enter_secant2(self, event):
        print('\nThe second secant modulus has been updated to ' + event.widget.get() + '%')
        shr_secant2.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_secant2) > 1:
    
            for i in range(Queue.qsize(shr_secant2)-1):
                remov = shr_secant2.get()

    def enter_secant3(self, event):
        print('\nThe third secant modulus has been updated to ' + event.widget.get() + '%')
        shr_secant3.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_secant3) > 1:
    
            for i in range(Queue.qsize(shr_secant3)-1):
                remov = shr_secant3.get()

    def enter_secant4(self, event):
        print('\nThe fourth secant modulus has been updated to ' + event.widget.get() + '%')
        shr_secant4.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_secant4) > 1:
    
            for i in range(Queue.qsize(shr_secant4)-1):
                remov = shr_secant4.get()

    def enter_stress_row(self, event):
        print('\nThe stress data row has been updated to ' + event.widget.get())
        shr_stress_row.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_stress_row) > 1:
    
            for i in range(Queue.qsize(shr_stress_row)-1):
                remov = shr_stress_row.get()

    def enter_stress_column(self, event):
        print('\nThe stress data column has been updated to ' + event.widget.get())
        shr_stress_column.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_stress_column) > 1:
    
            for i in range(Queue.qsize(shr_stress_column)-1):
                remov = shr_stress_column.get()

    def enter_time_row(self, event):
        print('\nThe time data row has been updated to ' + event.widget.get())
        shr_time_row.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_time_row) > 1:
    
            for i in range(Queue.qsize(shr_time_row)-1):
                remov = shr_time_row.get()

    def enter_time_column(self, event):
        print('\nThe time data column has been updated to ' + event.widget.get())
        shr_time_column.put(event.widget.get()) # Store user input values based upon enter key
  
        if Queue.qsize(shr_time_column) > 1:
    
            for i in range(Queue.qsize(shr_time_column)-1):
                remov = shr_time_column.get()

    def enter_tracker(self, event):
        print('\nThe tracker type has been updated to ' + event.widget.get())
        shr_tracker.put(event.widget.get()) # Store user input values based upon enter key

    def select_video(self):
        self.button1.configure(state='enabled')
        
        try:
            self.end()

        except RuntimeError:
            pass

        getPath()

    def start_Disable(self):
        self.button1.configure(state='disabled')
        self.button4.configure(state='disabled')
        self.button7.configure(state='enabled')
        self.start()

    def tracker1_Disable(self):
        self.button7.configure(state='disabled')
        self.button8.configure(state='enabled')
        tracker_Lock(0)

    def tracker2_Disable(self):
        self.button8.configure(state='disabled')
        tracker_Lock(1)
        self.button4.configure(state='enabled')

    def option_settings(self):
        self.toplevel3 = tk.Toplevel()
        self.img_Settings = tk.PhotoImage(file='Settings_Skin.png')
        self.settings_label = tk.Label(self.toplevel3, image=self.img_Settings)
        self.settings_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.settings_label.image = self.img_Settings
        self.toplevel3.title('Settings')
        self.toplevel3.resizable(width=False, height=False)

        self.toplevel3.configure(borderwidth='2', cursor='arrow', height='300', relief='raised')
        self.toplevel3.configure(width='500')

        bp = int(shr_bp.get()) # Break point
        shr_bp.put(bp)
        self.bp = tk.IntVar()
        self.bp.set(bp)
        self.entry4 = ttk.Entry(self.toplevel3, textvariable=self.bp) # Break point
        self.entry4.place(anchor='nw', relheight='0.08', relwidth='0.20', relx='0.35', rely='0.13', x='0', y='0')
        self.entry4.bind('<Return>', self.enter_bp)
        
        self.img_Info = tk.PhotoImage(file='Info_Button.png')
        self.button15 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button15.configure(image=self.img_Info, command=help_bp) # Break point
        self.button15.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.13', x='0', y='0')

        self.checkbutton1 = ttk.Checkbutton(self.toplevel3) # Auto break point detection
        self.checkbutton1.place(anchor='nw', relheight='0.1', relwidth='0.1', relx='0.68', rely='0.115', x='0', y='0')
        self.checkbutton1.state(['!alternate'])

        if auto_bp == 1:
            self.checkbutton1.state(['selected'])

        else:
            self.checkbutton1.state(['!selected'])

        self.checkbutton1.state(['disabled'])

        input_skip = int(shr_skip.get()) # Frame skipping
        shr_skip.put(input_skip)
        self.skip = tk.IntVar()
        self.skip.set(input_skip)
        self.entry8 = ttk.Entry(self.toplevel3, textvariable=self.skip, state='disabled') # Frame skipping
        self.entry8.place(anchor='nw', relheight='0.08', relwidth='0.20', relx='0.35', rely='0.23', x='0', y='0')
        self.entry8.bind('<Return>', self.enter_skip)

        self.button112 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button112.configure(image=self.img_Info, command=help_skipping) # Frame skipping
        self.button112.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.23', x='0', y='0')

        input_stress_row = int(shr_stress_row.get()) # Stress row
        shr_stress_row.put(input_stress_row)
        self.stress_row = tk.IntVar()
        self.stress_row.set(input_stress_row)
        self.entry9 = ttk.Entry(self.toplevel3, textvariable=self.stress_row) # Stress start row
        self.entry9.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.59', rely='0.855', x='0', y='0')
        self.entry9.bind('<Return>', self.enter_stress_row)

        input_stress_column = int(shr_stress_column.get()) # Stress column
        shr_stress_column.put(input_stress_column)
        self.stress_column = tk.IntVar()
        self.stress_column.set(input_stress_column)
        self.entry10 = ttk.Entry(self.toplevel3, textvariable=self.stress_column) # Stress start column
        self.entry10.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.71', rely='0.855', x='0', y='0')
        self.entry10.bind('<Return>', self.enter_stress_column)

        input_time_row = int(shr_time_row.get()) # Time row
        shr_time_row.put(input_time_row)
        self.time_row = tk.IntVar()
        self.time_row.set(input_time_row)
        self.entry11 = ttk.Entry(self.toplevel3, textvariable=self.time_row) # Time start row
        self.entry11.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.35', rely='0.855', x='0', y='0')
        self.entry11.bind('<Return>', self.enter_time_row)
        
        input_time_column = int(shr_time_column.get()) # Time column
        shr_time_column.put(input_time_column)
        self.time_column = tk.IntVar()
        self.time_column.set(input_time_column)
        self.entry12 = ttk.Entry(self.toplevel3, textvariable=self.time_column) # Time start column
        self.entry12.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.47', rely='0.855', x='0', y='0')
        self.entry12.bind('<Return>', self.enter_time_column)

        frac_stress = float(shr_frac_stress.get()) # Fraction stress
        shr_frac_stress.put(frac_stress)
        self.frac_stress = tk.DoubleVar()
        self.frac_stress.set(frac_stress)
        self.entry1 = ttk.Entry(self.toplevel3, textvariable=self.frac_stress) # Stress smoothing fraction
        self.entry1.place(anchor='nw', relheight='0.08', relwidth='0.20', relx='0.35', rely='0.615', x='0', y='0')
        self.entry1.bind('<Return>', self.enter_frac_stress)

        frac_strain = float(shr_frac_strain.get()) # Fraction strain
        shr_frac_strain.put(frac_strain)
        self.frac_strain = tk.DoubleVar()
        self.frac_strain.set(frac_strain)
        self.entry2 = ttk.Entry(self.toplevel3, textvariable=self.frac_strain) # Strain smoothing fraction
        self.entry2.place(anchor='nw', relheight='0.08', relwidth='0.20', relx='0.35', rely='0.515', x='0', y='0')
        self.entry2.bind('<Return>', self.enter_frac_strain)

        input_secant1 = int(shr_secant1.get()) # Secant 1
        shr_secant1.put(input_secant1)
        self.secant1 = tk.IntVar()
        self.secant1.set(input_secant1)
        self.entry3 = ttk.Entry(self.toplevel3, textvariable=self.secant1) # First secant modulus
        self.entry3.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.35', rely='0.715', x='0', y='0')
        self.entry3.bind('<Return>', self.enter_secant1)

        input_secant2 = int(shr_secant2.get()) # Secant 2
        shr_secant2.put(input_secant2)
        self.secant2 = tk.IntVar()
        self.secant2.set(input_secant2)
        self.entry5 = ttk.Entry(self.toplevel3, textvariable=self.secant2) # Second secant modulus
        self.entry5.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.47', rely='0.715', x='0', y='0')
        self.entry5.bind('<Return>', self.enter_secant2)

        input_secant3 = int(shr_secant3.get()) # Secant 3
        shr_secant3.put(input_secant3)
        self.secant3 = tk.IntVar()
        self.secant3.set(input_secant3)
        self.entry6 = ttk.Entry(self.toplevel3, textvariable=self.secant3) # Third secant modulus
        self.entry6.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.59', rely='0.715', x='0', y='0')
        self.entry6.bind('<Return>', self.enter_secant3)
        
        input_secant4 = int(shr_secant4.get()) # Secant 4
        shr_secant4.put(input_secant4)
        self.secant4 = tk.IntVar()
        self.secant4.set(input_secant4)
        self.entry7 = ttk.Entry(self.toplevel3, textvariable=self.secant4) # Fourth secant modulus
        self.entry7.place(anchor='nw', relheight='0.08', relwidth='0.10', relx='0.71', rely='0.715', x='0', y='0')
        self.entry7.bind('<Return>', self.enter_secant4)

        self.button16 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button16.configure(image=self.img_Info, command=help_file_type) # Stress file type
        self.button16.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.855', x='0', y='0')
        
        self.button17 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button17.configure(image=self.img_Info, command=help_frac_strain) # Strain fraction
        self.button17.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.515', x='0', y='0')       

        self.button17 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button17.configure(image=self.img_Info, command=help_frac_stress) # Stress fraction
        self.button17.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.615', x='0', y='0')     

        self.button18 = tk.Button(self.toplevel3, bg='white', relief='groove', borderwidth=2)
        self.button18.configure(image=self.img_Info, command=help_secant) # Secant modulus
        self.button18.place(anchor='nw', relheight='0.08', relwidth='0.05', relx='0.90', rely='0.715', x='0', y='0')

        self.menubar1 = tk.Menu(self.toplevel3) # GUI menu bar
        self.toplevel3['menu'] = self.menubar1
        
        self.filemenu1 = tk.Menu(self.menubar1, tearoff=0)
        self.filemenu1.add_command(label="Save Settings", command=save_Settings)
        self.menubar1.add_cascade(label='File', menu=self.filemenu1)

    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)

    def end(self):
        Thread(target=Extensometry).join()

    def start(self):
        self.refresh()

        Thread(target=Extensometry).start()

    def __init__(self):

        self.root = tk.Tk()
        self.root.withdraw() # Hide the root window

        # Build the GUI      
        self.toplevel1 = tk.Toplevel() # Building GUI using Toplevel
        self.img_Background = tk.PhotoImage(file='MAaD_Extensometry_Skin.png')
        self.background_label = tk.Label(self.toplevel1, image=self.img_Background)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.image = self.img_Background
        self.toplevel1.title('MAaD Extensometry: Video Extensometry using Computer Vision')
        self.toplevel1.iconphoto(True,tk.PhotoImage(file='MAaD_Science_Icon.png'))
        self.toplevel1.resizable(width=False, height=False)

        self.toplevel1.configure(borderwidth='2', cursor='arrow', height='600', relief='raised') # GUI frame
        self.toplevel1.configure(width='1000')
        self.toplevel1.protocol("WM_DELETE_WINDOW", self.closing)

        self.style = ttk.Style(self.toplevel1) # Button font
        self.style.configure("TButton", font=('Arial', 13), bordercolor='black', borderwidth=2)
        
        self.frame3 = ttk.Frame(self.toplevel1) # Message window frame
        self.frame3.configure(borderwidth='2', height='200', relief='groove', width='200')
        self.frame3.place(anchor='nw', bordermode='inside', relheight='0.47', relwidth='0.90', relx='0.05', rely='0.50', x='0', y='0')
        self.log_widget = ScrolledText(self.frame3, height=4, width=120, font=("consolas", "11", "normal"))
        self.log_widget.place(anchor='nw', relheight='0.93', relwidth='0.975', relx='0.01', rely='0.04', x='0', y='0')
        
        tracker_type = tk.StringVar()
        self.combobox1 = ttk.Combobox(self.toplevel1, textvariable=tracker_type) # Tracker type
        self.combobox1.place(anchor='nw', relheight='0.05', relwidth='0.15', relx='0.79', rely='.420', x='0', y='0')
        self.combobox1['values'] = ('CSRT','KCF')
        self.combobox1.current(0)
        self.combobox1.bind('<Return>', self.enter_tracker)

        self.img_Info1 = tk.PhotoImage(file='Info_Button.png')
        self.button111 = tk.Button(self.toplevel1, bg='white', relief='groove', borderwidth=2)
        self.button111.configure(image=self.img_Info1, command=help_tracker) # Tracker type
        self.button111.place(anchor='nw', relheight='0.04', relwidth='0.023', relx='0.918', rely='0.37', x='0', y='0')  

        self.button4 = ttk.Button(self.toplevel1, command=self.select_video, style='TButton') # Path button
        self.button4.configure(text='Select Video')
        self.button4.place(anchor='nw', relheight='0.1', relwidth='0.15', relx='0.07', rely='0.37', x='0', y='0')

        self.button1 = ttk.Button(self.toplevel1, command=self.start_Disable, style='TButton') # Start button
        self.button1.configure(text='Start', state='disabled')
        self.button1.place(anchor='nw', relheight='0.1', relwidth='0.15', relx='0.25', rely='0.37', x='0', y='0')

        self.button7 = ttk.Button(self.toplevel1, command=self.tracker1_Disable, style='TButton') # Tracker 1 lock button
        self.button7.configure(text='Lock Tracker 1', state='disabled')
        self.button7.place(anchor='nw', relheight='0.1', relwidth='0.15', relx='0.43', rely='0.37', x='0', y='0')

        self.button8 = ttk.Button(self.toplevel1, command=self.tracker2_Disable, style='TButton') # Tracker 2 lock button
        self.button8.configure(text='Lock Tracker 2', state='disabled')
        self.button8.place(anchor='nw', relheight='0.1', relwidth='0.15', relx='0.61', rely='0.37', x='0', y='0')

        logger = PrintLogger(self.log_widget) # Printing console commands to GUI
        sys.stdout = logger # Disable to show console
        sys.stderr = logger # Disable to show console

        welcome() # Welcome greeting

        self.menubar = tk.Menu(self.toplevel1) # GUI menu bar
        self.toplevel1['menu'] = self.menubar
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Help", command=help)
        self.filemenu.add_command(label="About", command=info)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Reset", command=rerun)
        self.filemenu.add_command(label="Quit", command=stop)
        self.menubar.add_cascade(label='File', menu=self.filemenu)

        self.optionmenu = tk.Menu(self.menubar, tearoff=0)
        self.optionmenu.add_command(label="Settings", command=self.option_settings)
        self.optionmenu.add_command(label="Strain-to-Stress", command=stress)
        self.menubar.add_cascade(label='Options', menu=self.optionmenu)
        
        self.root.mainloop()

# Define the extensometry function
class Extensometry():

    def __init__(self):

        # Pull in data from the GUI
        parameters() # Ensure only one item in queues and replace items

        bp = int(shr_bp.get()) # Break point
        shr_bp.put(bp)
        skip = int(shr_skip.get()) # Frame skipping
        shr_skip.put(skip)
        videoPath = shr_path.get() # Path to video
        shr_path.put(videoPath)
        trackerType = shr_tracker.get() # Tracker type
        shr_tracker.put(trackerType)
        
        if skip < 0:
            print('\nERROR: Frame skipping must be equal to or above 0')
            return
        
        if auto_bp == 0 or auto_bp == 1:
            pass
        else:
            print('\nERROR: Auto break point must be 0 or 1')
            return

        if bp <= 0:
            print('\nERROR: Break point must be greater than 0')
            return

        elif isinstance(bp, int) == False:
            print('\nERROR: Break point must be an integer')
            return

        # Update break point based upon frame skipping
        #bp = bp*(skip + 1)

        # Define result lists
        listtrack1 = list() # Top left pixel location for left gauge mark (row)
        listtrack2 = list() # Top left pixel location for left gauge mark (column)
        listtrack3 = list() # Bottom right pixel location for left gauge mark (row)
        listtrack4 = list() # Bottom right pixel location for left gauge mark (column)
        listtrack5 = list() # Top left pixel location for right gauge mark (row)
        listtrack6 = list() # Top left pixel location for right gauge mark (column)
        listtrack7 = list() # Bottom right pixel location for right gauge mark (row)
        listtrack8 = list() # Bottom right pixel location for right gauge mark (column)
        listtrack9 = list() # Left gauge mark location (row, average)
        listtrack10 = list() # Right gauge mark location (row, average)
        listtrack11 = list() # Gauge mark distance (pixel)
        listtrack12 = list() # Strain (%)
        listtrack13 = list() # Time (s)

        # Define headers
        listtrack1.append('NW Pixel Location - Row (Tracker 1)')
        listtrack2.append('NW Pixel Location - Column (Tracker 1)')
        listtrack3.append('SE Pixel Location - Row (Tracker 1)')
        listtrack4.append('SE Pixel Location - Column (Tracker 1)')
        listtrack5.append('NW Pixel Location - Row (Tracker 2)')
        listtrack6.append('NW Pixel Location - Column (Tracker 2)')
        listtrack7.append('SE Pixel Location - Row (Tracker 2)')
        listtrack8.append('SE Pixel Location - Column (Tracker 2)')
        listtrack9.append('Gauge Location of Tracker 1')
        listtrack10.append('Gauge Location of Tracker 2')
        listtrack11.append('Gauge Length (Pixels)')
        listtrack12.append('Strain (%)')
        listtrack13.append('Time (s)')

        temp = 1 # Loop counter

        # Establish the identity of the ojects across frames
        trackerTypes = ['CSRT','KCF']

        # Create a tracker based on tracker name
        def createTrackerByName(trackerType):
            if trackerType == 'CSRT':
                tracker = cv2.legacy.TrackerCSRT_create()
            elif trackerType == 'KCF': 
                tracker = cv2.legacy.TrackerKCF_create()
            else:
                tracker = None

            return tracker

        # Split the video name into a path and name component
        videoName = path.splitext(videoPath)[0]
        videoName = path.split(videoName)[1]

        # Append current date to output file
        currentDate = str(datetime.now())
        currentDate = currentDate[2:4:1] + currentDate[5:7:1] + currentDate[8:10:1]
        videoOut = videoName + "_Strain_" + currentDate + ".csv"

        # Create a video capture object to read videos
        cap = cv2.VideoCapture(videoPath)

        # Read first frame of the video
        success, frame = cap.read()

        # Quit if unable to read the video file
        if not success:
            print('\nERROR: Failed to read video type, reset app (File -> Reset) to update video')
            return

        # Determine frames-per-second of video
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Determine number of frames of video
        frames_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Select boxes
        bboxes = []
        colors = [] 

        j = 0

        print('\n1. Draw a box around the first gauge mark and press Lock Tracker 1')

        # Regions of interest selected based upon OpenCV
        while True:

            # Draw bounding boxes over objects
            bbox = cv2.selectROI('MAaD Extensometry at PNNL', frame, fromCenter=True)
            bboxes.append(bbox)
            colors.append((255,0,0))

            if j == 0:
                print('2. Draw a box around the second gauge mark and press Lock Tracker 2')

            elif j >= 2:
                sleep(2)
                break
            
            k = cv2.waitKey(0) & 0xFF

            j = j + 1

            if (k == 113):  # q is pressed
                break

        # Create object to track gauge marks
        track_Gauge = cv2.legacy.MultiTracker_create()

        # Initialize tracker 
        for bbox in bboxes:
            tracker = createTrackerByName(trackerType)
            if tracker is not None:
                 track_Gauge.add(tracker, frame, bbox)
            else:
                 print(f"Error: Unsupported tracker type '{trackerType}'")
                 return

        frame_number = 0 # Initialize the frame count
        frame_number_fps = 0 # Initialize frame count for fps
        tracker_not_located = 0 # Intialize variable to ensure object is being tracked
        skip_count = 0 # Initialize skip frame counter

        print('3. Extensometry analysis in progress: press ESC to quit and save results up to current frame')

        # Process video and track objects
        while cap.isOpened():
            
            # Capture analysis progress
            frame_progress = frame_number/frames_total         
            frame_number = frame_number + 1

            # Frame skipping
            if frame_number != 1:

                if skip != 0:
                    skip_count = skip_count + 1
                    
                    success = cap.grab()

                    if skip_count != skip:
                        skip_count = 0

                        continue
            
            success, frame = cap.read()

            if not success:
                break
            
            frame_number_fps = frame_number_fps + 1
            
            # Get updated location of objects in subsequent frames
            success, boxes = track_Gauge.update(frame)

            # Break out of while loop if tracking object is lost for three frames and remove false data
            if success == False:
                tracker_not_located = tracker_not_located + 1

                if tracker_not_located == 3 and auto_bp == 1:
                    del listtrack1[-3:]
                    del listtrack2[-3:]
                    del listtrack3[-3:]
                    del listtrack4[-3:]
                    del listtrack5[-3:]
                    del listtrack6[-3:]
                    del listtrack7[-3:]
                    del listtrack8[-3:]
                    del listtrack9[-3:]
                    del listtrack10[-3:]
                    del listtrack11[-3:]
                    del listtrack12[-3:]
                    del listtrack13[-3:]

                    break

            else:
                tracker_not_located = 0

            # Show and track objects
            for i, newbox in enumerate(boxes):

                if success == True:
                    colors[i] = (255,0,0)

                elif success == False:
                    colors[i] = (0,0,255)

                if i == 0:

                    # p1 and p2 are pixel locations for top left and bottom right corner of first box
                    p1 = (int(newbox[0]), int(newbox[1]))
                    p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                    cv2.rectangle(frame, p1, p2, colors[i], 1, 1) # Show box 1
                    p1 = str(p1)[1:-1]
                    p2 = str(p2)[1:-1]

                    # Pixel values stored in results lists for first box
                    listtrack1.append(p1.split(", ",1)[0])
                    listtrack2.append(p1.split(", ",1)[1])
                    listtrack3.append(p2.split(", ",1)[0])
                    listtrack4.append(p2.split(", ",1)[1])
                    listtrack9.append((int(p2.split(", ",1)[0])+int(p1.split(", ",1)[0]))/2)

                    cv2.line(frame,(int(listtrack9[temp]),int(listtrack4[temp])-75),(int(listtrack9[temp]),int(listtrack2[temp])+75),colors[i],1) # Draw gauge line for first box

                else:

                    # p3 and p4 are pixel locations for top left and bottom right corner of second box
                    p3 = (int(newbox[0]), int(newbox[1]))
                    p4 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                    cv2.rectangle(frame, p3, p4, colors[i], 1, 1) # Show box 2
                    p3 = str(p3)[1:-1]
                    p4 = str(p4)[1:-1]

                    # Pixel values stored in results lists for second box
                    listtrack5.append(p3.split(", ",1)[0])
                    listtrack6.append(p3.split(", ",1)[1])
                    listtrack7.append(p4.split(", ",1)[0])
                    listtrack8.append(p4.split(", ",1)[1])
                    listtrack10.append((int(p4.split(", ",1)[0])+int(p3.split(", ",1)[0]))/2)

                    cv2.line(frame,(int(listtrack10[temp]),int(listtrack8[temp])-75),(int(listtrack10[temp]),int(listtrack6[temp])+75),colors[i],1) # Draw gauge line for second box

            # Determine the gauge separation and strain
            if i != 1:
                break # Break out while loop if more than two boxes created

            else:
                listtrack11.append(abs((int(p4.split(", ",1)[0])+int(p3.split(", ",1)[0]))/2-(int(p2.split(", ",1)[0])+int(p1.split(", ",1)[0]))/2))
                listtrack12.append(100*(abs((int(p4.split(", ",1)[0])+int(p3.split(", ",1)[0]))/2-(int(p2.split(", ",1)[0])+int(p1.split(", ",1)[0]))/2)-listtrack11[1])/listtrack11[1])

            # Break out of while loop if pixel displacement greater than break point
            if temp > 1:
                if abs(listtrack11[temp] - listtrack11[temp-1]) > bp:
                    break

            # Determine time for each frame
            if skip == 0:
                listtrack13.append((frame_number-1)/fps)

            else:
                listtrack13.append((frame_number-1)*(1+1/(skip+1))/fps)

            # Show frame
            cv2.imshow('MAaD Extensometry at PNNL', frame)

            # Quit on ESC button
            if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
                break

            temp =  temp + 1 # Increase loop counter (each frame)

        # Combine and output results into CSV
        data_list = list(zip(listtrack13, listtrack11, listtrack12))

        # Output results in *.csv
        with open(videoOut, "w") as f:
            writerOut = writer(f, lineterminator = '\n')

            for row in data_list:
                writerOut.writerow(row)

        # Indicate analysis completed successfully
        print('\nCOMPLETED video extensometry analysis:')
        print(' - Selected tracker type of ' + str(trackerType))
        print(' - Break point of ' + str(int(bp)) + ' pixels')
        print(' - Auto break point was set to ' + str(auto_bp))
        print(' - Frame skipping was set to ' + str(skip))
        
        cv2.destroyAllWindows()

# Start the app
if __name__ == "__main__":

    # Define datasharing between threads and set default values
    shr_path = Queue()
    root_directory = os.path.dirname(os.path.abspath(__file__))
    shr_path.put(str(root_directory))
    shr_tracker = Queue()
    shr_tracker.put(tracker)
    shr_bp = Queue()
    shr_bp.put(bp)
    shr_skip = Queue()
    shr_skip.put(skip)
    shr_frac_strain = Queue()
    shr_frac_strain.put(frac_strain)
    shr_frac_stress = Queue()
    shr_frac_stress.put(frac_stress)
    shr_secant1 = Queue()
    shr_secant1.put(secant1)
    shr_secant2 = Queue()
    shr_secant2.put(secant2)   
    shr_secant3 = Queue()
    shr_secant3.put(secant3)
    shr_secant4 = Queue()
    shr_secant4.put(secant4)
    shr_stress_row = Queue()
    shr_stress_row.put(stress_row)
    shr_stress_column = Queue()
    shr_stress_column.put(stress_column)   
    shr_time_row = Queue()
    shr_time_row.put(time_row)
    shr_time_column = Queue()
    shr_time_column.put(time_column)

    app = App() # Run app