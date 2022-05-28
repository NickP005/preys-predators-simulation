import random
import math
import numpy as np
import copy

#here there is the brain

#create a brain structure
#input[] which is the
# rays distances (6), rays angles, speed, angle, energy
test_input = [400, 400, 400, 400, 400, 400, -60, -40, -20, +20, +40, +60, 50, 20, 80, 200]

# accelleration (max 10), angle change(0->360)
example_output = [8, 30]

class brain:
    def __init__(self, layers):
        self.nodes = populate_nodes(layers)
        self.many_layers = self.compute_many_layers(self.nodes)
        self.connections = populate_connections(5, self.nodes)
        self.many_nodes = len(self.nodes)

    def compute_many_layers(self, nodes):
        many_layers = 0
        for node in nodes.values():
            if(node.layer > many_layers):
                many_layers =  node.layer
        return many_layers
    def compute_output(self, input_values):
        #substitute to all the first layer nodes the inputs as values
        for node in self.nodes.values():
            if(node.id < len(input_values)):
                node.value = input_values[node.id]
            else:
                node.value = 0
        #now compute all the values for all the layers
        for layer_id in range(1, self.many_layers + 1):
            #for each connection check that the "to" node goes to
            # a node of the layer. then add to that node the value multiplied
            #after all for each node of the layer apply the sigmoid function
            for connection in self.connections:
                if(connection.to_id not in self.nodes.keys() or connection.from_id not in self.nodes.keys()):
                    del connection
                    continue
                if(self.nodes[connection.to_id].layer == layer_id):
                    self.nodes[connection.to_id].value += self.nodes[connection.from_id].value * connection.weight
            for id, node in self.nodes.items():
                if(node.layer == layer_id and layer_id != self.many_layers):
                    self.nodes[id].value = 1 / (1 + np.exp(-node.value))
        #now compute the output for our little creatures
        accelleration = self.nodes[20].value
        direction = self.nodes[21].value
        """
        for id, node in self.nodes.items():
            print("#",id, " ", node.value)
        print("CONNECTIONS")
        for connection in self.connections:
            print("#",connection.from_id, " -> #", connection.to_id, " ", connection.weight)
        """
        return (direction, accelleration)

#then we have X inner nodes
class inner_node:
    def __init__(self, id, bias=10, layer=1):
        self.id = id
        self.bias = bias
        self.layer = layer
        self.value = 0.8

class connection:
    def __init__(self, from_id, to_id, weight):
        self.from_id = from_id
        self.to_id = to_id
        self.weight = weight

def populate_nodes(layers):
    nodes = {}
    iter = 0
    for layer_id in range(len(layers)):
        for id in range(layers[layer_id]):
            nodes[iter] = inner_node(iter, 5, layer_id)
            iter += 1
    return nodes

#makes X random connections between nodes
def populate_connections(many, nodes, check=True):
    connections = []
    iterations = 0
    while(len(connections) < many and iterations < 100):
        random_from = random.randint(0, len(nodes)-1)
        random_to = -1
        iterations2 = 0
        while(random_to == -1 or random_to == random_from):
            random_to = random.randint(0, len(nodes)-1)
            if(random_to not in nodes or random_from not in nodes):
                continue
            if(nodes[random_to].layer <= nodes[random_from].layer):
                random_to = -1
            if(iterations2 > 100):
                break
            iterations2 += 1
        if(iterations2 > 100):
            continue
        random_weight = random.uniform(-5, +5)
        conn = connection(random_from, random_to, random_weight)
        if not check:
            connections.append(conn)
        if(is_unique_connection(conn, connections) and check):
            connections.append(conn)
        iterations += 1
    return connections

def is_unique_connection(connection, connections):
    for connection_i in connections:
        if(connection_i.from_id == connection.from_id and connection_i.to_id == connection.to_id):
            return False
    return True

def mutation_of(brainl):
    brain = copy.deepcopy(brainl)
    #now make random nodes. 1new layer 2existing layer 3-6nothing
    switch = random.randint(0,5)
    if(switch == 0):
        #change the final nodes layer, take their id and change connections
        for id, node in brain.nodes.items():
            if(node.layer == brain.many_layers):
                node.layer += 1
        brain.nodes[brain.many_nodes] = inner_node(brain.many_nodes, 5, brain.many_layers)
        brain.many_layers += 1
        brain.many_nodes += 1
    elif(switch == 1):
        random_layer = random.randint(1,brain.many_layers)
        brain.nodes[brain.many_nodes] = inner_node(brain.many_nodes, 5, random_layer)
        brain.many_nodes += 1
    elif(switch ==2):
        random_to_delete = random.randint(16,brain.many_nodes)
        while(random_to_delete in [20,21]):
            random_to_delete = random.randint(16,brain.many_nodes)
        to_delete = []
        if(random_to_delete in brain.nodes.keys()):
            del brain.nodes[random_to_delete]
        for connection_id in range(len(brain.connections)):
            connection = brain.connections[connection_id]
            if(connection.from_id == random_to_delete or connection.to_id == random_to_delete):
                to_delete.append(connection_id)
        cache_list = []
        for i in range(len(brain.connections)):
            if i not in to_delete:
                cache_list.append(brain.connections[i])
        brain.connections = cache_list

    #1make connection 2make, if already present, destroy 3destroy connection 4-5do nothing
    switch = random.randint(0,6)
    if(switch == 0 or switch == 1):
        connections_list = populate_connections(1, brain.nodes, True)
        brain.connections.append(connections_list[0])
    elif(switch == 2):
        connections_list = populate_connections(1, brain.nodes, False)
        if(is_unique_connection(connections_list[0], brain.connections)):
            brain.connections.append(connections_list[0])
        else:
            for i in range(len(brain.connections)):
                connection_i = brain.connections[i]
                if(connection_i.from_id == connections_list[0].from_id and connection_i.to_id == connections_list[0].to_id):
                    del brain.connections[i]
                    break
    elif switch == 3:
        if(len(brain.connections) > 2):
            del brain.connections[random.randint(0, len(brain.connections)-1)]
    elif switch == 4:
        if(len(brain.connections) > 2):
            ran = random.randint(0,len(brain.connections)-1)
            brain.connections[ran].weight += random.uniform(-2, +2)
            if brain.connections[ran].weight > 5:
                brain.connections[ran].weight = 5
            elif brain.connections[ran].weight < 5:
                brain.connections[ran].weight = -5
    return brain



#test_brain = brain([(6+6+2+1), 4, (1+1)])
#out = test_brain.compute_output(test_input)
#print(out[0], out[1])
