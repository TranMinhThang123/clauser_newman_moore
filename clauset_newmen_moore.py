
#!/usr/bin/env python
 
'''
Usage:
    python cnm.py <input_file> <output_file>
'''
 
import heapq
import sys
import time
from utils import DFS
def read_input(filename):
    ''' Loads the input into a dictionary'''
 
    output_dict = {}
    with open(filename, 'r') as f:
        for line in f:
            l = line.split('\t')
            key = int(l[0].strip())
            value = int(l[1].strip())
 
            if key not in output_dict:
                output_dict[key] = []
            if value not in output_dict:
                output_dict[value] = []
 
            if value in output_dict[key]:
                pass
            else:
                output_dict[key].append(value)
 
            if key in output_dict[value]:
                pass
            else:
                output_dict[value].append(key)
 
    return output_dict
 
 
def calculate_m(input_dict):
    ''' Gives the total number of edges in the network. '''
    total = 0
    for key in input_dict:
        total += len(input_dict[key])
    return total / 2
 
 
def calculate_deltaQ(m, ki, kj):
    ''' Calculates deltaQ for two communities i and j '''
    deltaQ = 1.0/(2.0*m) - float(ki*kj) / ((2*m)**2)
    return deltaQ
 
 
def populate_Qtrees(input_dict, m):
    Qtrees = {}
    for i in input_dict:
        community = input_dict[i]
        ki = len(community)
        Qtrees[i] = {}
        for j in community:
            kj = len(input_dict[j])
            Qtrees[i][j] = calculate_deltaQ(m, ki, kj)
 
    return Qtrees
 
 
def populate_Qheaps(input_dict, m):
    Qheaps = {}
    for key in input_dict:
        community = input_dict[key]
        ki = len(community)
        Qheaps[key] = []
        for i in community:
            kj = len(input_dict[i])
            deltaQ = calculate_deltaQ(m, ki, kj)
            # we store the items in the heap as their negative values because
            # python heap is a min-heap
            heapq.heappush(Qheaps[key], (-deltaQ, i, key))
    return Qheaps
 
 
def populate_H(Qheaps):
    H = []
    for key in Qheaps:
        if Qheaps[key] == []:
            continue
        else:
            maximum = Qheaps[key][0]
        heapq.heappush(H, maximum)
    return H
 
 
def populate_a(input_dict, m):
    a = {}
    for key in input_dict:
        k = len(input_dict[key])
        ai = float(k) / (2.0 * m)
        a[key] = ai
    return a
 
 
def select_largest_q(H):
    return heapq.heappop(H)
 
 
def update_Qtrees(Qtrees, a, i, j):
 
    # from equation 10a - summing i into j
    for key in Qtrees[i]:
        if key in Qtrees[j]:
            Qtrees[j][key] = Qtrees[i][key] - Qtrees[j][key]
 
    # from equations 10b and 10c - update row j
    for key in Qtrees:
        if key in Qtrees[i] and key not in Qtrees[j]:
            Qtrees[j][key] = Qtrees[i][key] + (2 * a[j] * a[key])
        elif key in Qtrees[j] and key not in Qtrees[i]:
            Qtrees[j][key] = Qtrees[j][key] + (2 * a[i] * a[key])
 
    # remove i for each row k and update j for each row k
    for key in Qtrees:
        if i in Qtrees[key]:
            Qtrees[key].pop(i, None)
        if j in Qtrees[key]:
            Qtrees[key][j] = Qtrees[key][j] + (2 * a[i] * a[key])
 
    # remove the self-reference (necessary because our tree is a python dict)
    # for example i == j
    if j in Qtrees[j]:
        Qtrees[j].pop(j, None)
 
    # remove i from entire tree
    Qtrees.pop(i, None)
 
    return Qtrees
 
 
def update_Qheaps(Qtrees, Qheaps, i, j):
 
    # remove the heap i
    Qheaps.pop(i, None)
 
    # rebuild the jth heap from the jth binary tree in Qtree
    community = Qtrees[j]
    h = [ (community[key], key, j) for key in community ] # list comprehension
    heapq.heapify(h)
    Qheaps[j] = h
 
    # remove the ith and update the jth element in each heap
    for key in Qheaps:
        heap = Qheaps[key]
        for item in heap[:]:
            if item[1] == i:
                heap.remove(item)
                heapq.heapify(heap)
            elif item[1] == j:
                # we temporarily change the item to a list to perform insertion
                # (tuples are immutable)
                item_copy = list(item)
                heap.remove(item)
                heapq.heapify(heap)
                item_copy[0] = Qtrees[key][j]
                heapq.heappush(heap, tuple(item_copy))
 
    return Qheaps
 
 
def update_a(a, i, j):
    a[j] += a[i]
    a[i] = 0
    return a
 


def main():
    ''' Main loop of the program. '''
 
    # read command line input
    filename = sys.argv[1]
    maxQ = 0
    max_step = 0
    Q = 0
 
    input_dict = read_input(filename)
    print("INPUT DICT:")
    print(input_dict)
    m = calculate_m(input_dict)
    nodes = len(input_dict)
 
    Qtrees = populate_Qtrees(input_dict, m)
    Qheaps = populate_Qheaps(input_dict, m)
    # print("Q TREE:")
    # print(Qtrees)
    # print("Q HEAP:")
    # print(Qheaps)

    H = populate_H(Qheaps)
    a = populate_a(input_dict, m)
 
    step = 0
    
    adjacency_list = dict(zip([i+1 for i in range(nodes)],[[] for _ in range(nodes)]))
    print(adjacency_list)

    print('i', '\t', 'j', '\t', 'Q', '\t\t', 'deltaQ', '\t\t', 'step')

    while H:
        deltaQ, i, j = select_largest_q(H)
        Q -= deltaQ


        Qtrees = update_Qtrees(Qtrees, a, i, j)
        Qheaps = update_Qheaps(Qtrees, Qheaps, i, j)
        H = populate_H(Qheaps)
        a = update_a(a, i, j)

        step += 1

        print(i, '\t', j, '\t', round(Q, 7), '\t', round(deltaQ, 7), '\t', step)
 
        if deltaQ < 0:
            maxQ = deltaQ
            max_step = step
            adjacency_list[i].append(j)
            adjacency_list[j].append(i)
        else:
            pass

    output_file = sys.argv[2]
    with open(output_file, 'w+') as f:
        f.write(
'''FASTCOMMUNITY_INFERENCE_ALGORITHM in python!
START-----: {0}
---NET_STATS----
NUMNODES--: {1}
NUMEDGES--: {2}
---MODULARITY---
MAXQ------: {3}
STEP------: {4}
'''.format(time.asctime(),
                          nodes,
                          m,
                          maxQ,
                          max_step))
    dfs = DFS(adjacency_list)
    components = dfs.get_connected_component()
    with open(output_file,'a') as f:
        f.write('''---CLUSTERS---
''')
        for i in components:
            # print(f"CLUSTER {i}: ",components[i])
            f.write("CLUSTER "+str(i)+": "+",".join([str(node) for node in components[i]])+'\n')
        f.write('''EXIT------: {}'''.format(time.asctime()))
 
 
if __name__ == '__main__':
    main()