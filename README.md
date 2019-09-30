Author: Vedran Furtula
Date: 26 Sept 2019

Welcome to the Swanepoel method analysis python code. This is just one way out of numerous ways to implement this method. The Swanepoel method is based on an article with a title "Determination of the thickness and optical constants of amorphous silicon" written by R. Swanepoel in 1983.

####################################################

################### RUN THE CODE ###################

####################################################

In order to run the program in Windows type use the Anaconda prompt:
python Run_GUI.py

In order to run the program in Linux type:
python3 Run_GUI.py

The folder named "Data" contains many sets of measured data from the OLIS and the FTIR. If you have any new sets of data please put those file in this folder.

The folder named "Results" contains some examples of post processed data originally coming from the OLIS and the FTIR. Keep this folder as your data post processed folder in order to keep files and folders tidy in the entire working folder. Otherwise, you can store your post processed data anywhere by filling in the location in the "STORAGE location" edit field on the bottom of the GUI, ie. if the folder entered in this field is not existing it will be created for you.

############################################

################### HELP ###################

############################################

All the individual functions/steps shown in the GUI are explained in the help menu found on the main bar.

#####################################################

################ INSTALL FOR WINDOWS ################

#####################################################

To run the code in Windows install Anaconda for Python 3:
https://www.anaconda.com/distribution/

###################################################

################ INSTALL FOR LINUX ################

###################################################

To run the code in Linux first make sure that you have Python 3 is installed:
https://docs.python-guide.org/starting/install3/linux/

For Linux users, make sure to install all the necessary Python modules such as numpy, matplotlib, scipy, yagmail using "pip3 install [module]".
