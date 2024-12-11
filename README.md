# CapstoneProject

This project is an automated price tracker for amazon products. This tracks price at certain times of the day, every 6 hours starting at 1:00am EST. The program scrapes the data from the website and logs it into a .csv file named "price_history.csv", this file is also used to generate 3 seperate graphs using matplotlib in real time. 

There are seperate files for each use. the generate_data.py file is the main file code. This code accesses the websites requested and scrapes the data for storage.

The graph.py generates 4 seperate graphs through matplotlab and seaborn.



The .json file is the GUI to add and delete products from the tracker. 