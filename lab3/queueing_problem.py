'''
Queueing Problem
Author: doodhwala

Drive-in Restaurant simulation
Abdul-Bakra at the counters

'''

import random
import sys
import csv

M = 2
N = 26

MAX_SIMULATION_TIME = 60
service_time_digits = 2
arrival_time_digits = 2

arrival_times = []

def table_lookup(table, value):
    for row in table:
        l, r = row[3], row[4]
        if(l <= value <= r):
            return row[0]

with open('input.in', 'r') as f:
    lines = f.read().split('\n')
    times = int(lines[0])
    cp = 0.0
    rd = 1
    for t in range(1, times + 1):
        time, prob = lines[t].split()
        time, prob = int(time), float(prob)
        cp += prob
        rd_range = int(prob * 10**arrival_time_digits)
        arrival_times.append((time, prob, cp, rd, rd + rd_range - 1))
        rd += rd_range

    M = int(lines[times+1])
    lines = lines[times+2:]

    counters = [{"free" : True, "time_when_free" : 0} for i in range(M)]
    for i in range(M):
        name, times = lines[0].split()
        times = int(times)
        service_times = []
        cp = 0.0
        rd = 1
        for t in range(1, times + 1):
            time, prob = lines[t].split()
            time, prob = int(time), float(prob)
            cp += prob
            rd_range = int(prob * 10**service_time_digits)
            service_times.append((time, prob, cp, rd, rd + rd_range - 1))
            rd += rd_range
        counters[i]['name'] = name
        counters[i]['service_times'] = service_times
        lines = lines[times+1:]

# Generating data for simulation
arrival_random = [0, 26, 98, 90, 29, 42, 74, 80, 68, 22, 48, 34, 45, 24, 34, 63, 38, 80, 42, 56, 89, 18, 51, 71, 16, 92]
service_random = [95, 21, 51, 92, 89, 38, 13, 61, 50, 49, 39, 53, 88, 1, 81, 53, 81, 64, 1, 67, 1, 47, 75, 57, 87, 47]
customers = []
for i in range(N):
    # r_arrival = random.randint(1, 10**arrival_time_digits)
    # r_service = random.randint(1, 10**service_time_digits)
    r_arrival = arrival_random[i]
    r_service = service_random[i]
    customers.append((r_arrival, r_service))

time = 0
for i in range(N):
    customer = i+1
    time_since_last_arrival = table_lookup(arrival_times, customers[i][0])
    if(i == 0):
        time_since_last_arrival = 0
    arrival_time = time + time_since_last_arrival
    time = arrival_time

    customer = {
        "customer": customer,
        "time_since_last_arrival" : time_since_last_arrival,
        "arrival_time" : arrival_time,
        "service_time_digits" : customers[i][1]
    }
    customers[i] = customer

# Since Abdul has a lower counter number, he is selected in preference to Bakra
def find_next_free_counter(time):
    next_free = (-1, sys.maxsize)
    for i in range(M):
        if counters[i]["free"]:
            next_free = (i, time)
        else:
            if(next_free[1] > counters[i]["time_when_free"]):
                next_free = (i, counters[i]["time_when_free"])
    return next_free

def update_counters_till(t):
    for counter in counters:
        if(t >= counter["time_when_free"]):
            counter["free"] = True

time = 0
for i in range(N):
    this_customer = customers[i]
    time = this_customer["arrival_time"]
    if(time > MAX_SIMULATION_TIME):
        break
    update_counters_till(time)
    assigned_counter = find_next_free_counter(time)
    this_customer["counter"] = assigned_counter[0]
    this_customer["service_time"] = table_lookup(counters[this_customer["counter"]]["service_times"], customers[i]["service_time_digits"])
    this_customer["time_in_queue"] = assigned_counter[1] - time
    this_customer["time_service_begins"] = assigned_counter[1]
    this_customer["time_service_ends"] = this_customer["time_service_begins"] + this_customer["service_time"]
    this_customer["time_in_system"] = this_customer["time_in_queue"] + this_customer["service_time"]
    counter = counters[this_customer["counter"]]
    counter["free"] = False
    counter["time_when_free"] = this_customer["time_service_ends"]


'''
Customer, Time since last arrival, arrival time, service time, time service begins, time customer waits in queue, time service ends, time customer spends in system, ~idle time of server
'''

keys = ['customer', 'time_since_last_arrival', 'arrival_time', 'time_service_begins', 'service_time', 'time_service_ends', 'time_service_begins', 'service_time', 'time_service_ends', 'time_in_queue', 'time_in_system']

key_pretty = {
    'customer' : 'Customer',
    'time_since_last_arrival'  : 'Time Since Last Arrival',
    'arrival_time'  : 'Arrival Time',
    'service_time'  : 'Service Time',
    'time_service_begins'  : 'Time Service Begins',
    'time_in_queue'  : 'Time in Queue',
    'time_service_ends'  : 'Time Service Ends',
    'time_in_system'  : 'Time in System'
}

with open('simulation.csv', 'w', newline='') as csvfile:
    sheet = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    sheet.writerow([key_pretty[key] for key in keys])
    for customer in customers:
        raw_row = [customer[key] for key in keys]
        if(customer["counter"] == 0):
            raw_row[6:9] = ['-', '-', '-']
        else:
            raw_row[3:6] = ['-', '-', '-']
        sheet.writerow(raw_row)
