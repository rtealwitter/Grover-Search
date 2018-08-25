# R. Teal Witter
# Completed May 2018 for Quantum Computing at Middlebury College
# Implements grover search on a simulated quantum computer

from pyquil.quil import Program
from pyquil.api import get_devices, QVMConnection
from pyquil.gates import *
import numpy as np
import time
import random

# working qubits at the time
valid = [11,6,16,17,10,12,7,1,5,0]                        # valid qubits with connection

def setup(n, s):
    """ function to set up program Uf and special unitary """
    p = Program()                                         # initializes program

    Uf = np.identity(2 ** (n + 1))                        # starts Uf as identity with size 2^ (n + 1)
    Uf[:,[2 * s, 2 * s + 1]] = Uf[:,[2 * s + 1, 2 * s]]   # switch the columns of the s^th qubit
    p.defgate("Uf", Uf)                                   # defines array as unitary Uf

    special = -1 * np.identity(2 ** n)                    # starts special as negative identity with size 2^n
    special[0,0] = 1                                      # makes the very first entry positive
    p.defgate("special", special)                         # defines array as unitary special

    return p

def new_range(num):
    """ account for dead connections in 19Q-Acorn """
    return valid[:num]              # returns subset of valid qubits

def to_num(result):
    """ converts binary list to decimal number """
    return int(str(result).strip('[]').replace(', ', ''), 2) # clean list then turn it into int

def bits(l):
    """ returns l nams of l bits """
    lst = str(list(new_range(l)))              # converts list of new_range to string
    return lst.strip('[]').replace(',','')     # returns that string without the brackets or commas

def apply_H(p, n):
    """ applies Hadamard to n qubits """
    for i in new_range(n):                     # loops n times over new_range
        p.inst(H(i))                           # applies H to i^th qubit
    return p
    
def grover(n, s):
    """ grover algorithm for finding s """
    p = setup(n,s)                          # sets up program to access api

    repeats = int(np.floor(np.pi * 2 ** (n / 2.0) / 4.0)) # calculate number of repeats

    p = apply_H(p, n)                       # prepares 0s with H applied to each
    p.inst(X(valid[n]))                     # prepares last qubit into 1
    p.inst(H(valid[n]))                     # then -

    for i in range(repeats):                # loops repeats times
        p.inst(("Uf " + bits(n+1)))         # applies Uf to all qubits
        p = apply_H(p, n)                   # applies H to all but last qubit
        p.inst(("special " + bits(n)))      # applies special to all but last qubit
        p = apply_H(p, n)                   # applies H to all but last qubit

    position = 0
    for i in new_range(n):                  # measures all but last qubit
        p.measure(i, position)              # stores outcomes in normal registers
        position += 1                       # stores in first qubits for simpler reading

    return p                                # returns program p

def accuracy(result, s):
    """ calculates accuracy over all trial times """
    correct = 0.0                    # initializes number of correct to 0 double for division
    for i in range(len(result)):     # loops over all trails
        if to_num(result[i]) == s:   # checks if correct output
            correct += 1             # increments correct if correct output
    return correct / len(result)     # returns fractional success

def without_error(n, s, runs):
    """ runs grover on 2^n qubits without error simulation """
    qvm = QVMConnection(use_queue = False)             # put in queue in case too long
    p = grover(n, s)                                   # stores grover program
    result = qvm.run(p, list(range(n)), trials = runs) # stores result
    print(accuracy(result, s))                         # prints accuracy rate


def with_error(n, s, runs): 
    acorn = get_devices(as_dict = True)['19Q-Acorn']             # simulate noise with 19Q-Acorn
    qvm = QVMConnection(acorn, use_queue = True)                 # put in queue in case too long
    p = grover(n, s)                                             # stores grover program
    job_id = qvm.run_async(p, list(range(n)), trials = runs)     # stores result
    job = qvm.get_job(job_id)                                    # stores job
    while not job.is_done():                                     # while the job isn't finished
        time.sleep(.1)                                           # wait .1 seconds
        job = qvm.get_job(job_id)                                # update job status
    result = job.result()                                        # store job result
    print(accuracy(result, s))                                   # prints accuracy rate

for i in range(1, 5): 
    without_error(i, random.randint(0, 2 ** i - 1), 1000)
    # with_error(i, 1, 1000)
