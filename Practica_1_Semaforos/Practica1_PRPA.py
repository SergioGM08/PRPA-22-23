# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:21:20 2023

@author: Sergio
"""
from multiprocessing import Process, Manager
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array, Value
import random


NPROD = 5 #Número de productores
NCONS = 1 #Número de consumidores
N = 5 #Elementos por productor

def producer(pid, last_val, storage, empty, non_empty):
    for i in range(N):
        empty.acquire()
        data = last_val.value + random.randint(0, 100)
        print (f"Producer {current_process().name} is producing {data}")
        storage[pid] = data
        print (f"Producer {current_process().name} is storing: {data} \n")
        non_empty.release()
            
    empty.acquire()
    storage[pid] = -1 #Cuando un proceso ha terminado, escribimos -1
    non_empty.release()
    
def consumer(storage,last_val, in_order, empty, non_empty):

    for s in non_empty: 
        s.acquire()
        print (f"Consumer {current_process().name} is unstoring")
    count = 0
    while is_there_room(storage):
        data = take_min(storage) #Coge el mínimo del almacén
        last_val.value = data
        in_order.append(data) #Añade el mínimo a la lista ordenada
        ind = (storage[:]).index(data) #Coge el índice del mínimo del almacén
        storage[ind] = -2 #Posición vacía después de cogerlo
        empty[ind].release()
        print (f"\n Consumer {current_process().name} is consuming {data} in position {count}")
        count += 1
        non_empty[ind].acquire()

    print(f" \n In order:\n {in_order} \n")

    
def take_min(storage): #Buscamos el mínimo y que sea aceptable
    minima = []
    
    for i in range(NPROD):
        
        if storage[i]<0:
            minima.append(max(storage) + 1)
            
        else:
            minima.append(storage[i])
            
    return min(minima)

def is_there_room(storage): #Si storage no vacío
    control = False
    
    for i in range(NPROD):
        
        if storage[i] != -1:
            control = True
            
    return control       
            

def main():
    storage = Array('i', NPROD)
    last_val = Value('i',0)
    for i in range(NPROD):
        storage[i] = -2 #Convenimos que -2 indica que está vacío
        
    print ("Initial storage", storage[:])
        
    empty = [Lock() for i in range(NPROD)]
    non_empty = [Semaphore(0) for i in range(NPROD)]
    manager = Manager()
    in_order=manager.list()
    
    prodlst = [Process(target = producer,
                       name = f'prod_{i}',
                       args = (i,last_val, storage, empty[i], non_empty[i]))
               for i in range(NPROD)]

    cons = Process(target = consumer,
                   name = 'cons_x',
                   args = (storage,last_val, in_order, empty, non_empty))

    for p in prodlst + [cons]:
        p.start()

    for p in prodlst + [cons]:
        p.join()

if __name__ == '__main__':
    main()