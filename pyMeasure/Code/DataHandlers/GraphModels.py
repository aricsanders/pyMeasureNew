#-----------------------------------------------------------------------------
# Name:        GraphModels
# Purpose:     To store graphs used in network translations
# Author:      Aric Sanders
# Created:     4/6/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" Graph Models stores sub classes of graphs that define data translations """

#-----------------------------------------------------------------------------
# Standard Imports
import re
import datetime

#-----------------------------------------------------------------------------
# Third Party Imports
try:
    from pyMeasure.Code.Utils.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
try:
    from pyMeasure.Code.DataHandlers.GeneralModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.GeneralModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    from pyMeasure.Code.DataHandlers.TouchstoneModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.TouchstoneModels was not found,"
          "please put it on the python path")
    raise ImportError

try:
    import numpy as np
except:
    print("The module numpy was not found,"
          "please put it on the python path")
    raise ImportError

#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def edge_1_to_2(in_string):
    return in_string.splitlines()

def edge_2_to_1(string_list):
    return string_list_collapse(string_list)
#-----------------------------------------------------------------------------
# Module Classes
class Graph():
    def __init__(self,**options):
        """Initializes the graph. The first 2 nodes and two edges forming a bijection between them are required"""
        defaults={"graph_name":"Graph",
                  "node_names":['n1','n2'],
                  "node_descriptions":{'n1':"A plain string",
                                       'n2':"A list of strings with no \\n, created with string.splitlines()"},
                  "current_node":'n1',
                  "state":[1,0],
                  "data":"This is a test string\n it has to have multiple lines \n and many characters 34%6\n^",
                  "edge_2_to_1":edge_2_to_1,
                  "edge_1_to_2":edge_1_to_2
                 }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        self.elements=['graph_name','node_names','node_descriptions','current_node','state','data']
        for element in self.elements:
            self.__dict__[element]=self.options[element]
        self.edges=[]
        self.edge_matrices=[]
        self.state_matrix=np.matrix(self.state).T
        # Add the first 2 edges, required to intialize the graph properly
        self.add_edge(self.node_names[0],self.node_names[1],self.options["edge_1_to_2"])
        self.add_edge(self.node_names[1],self.node_names[0],self.options["edge_2_to_1"])

    def set_state(self,node_name,node_data):
        """Sets the graph state to be the state specified by node_name, and node_data"""
        try:
            current_node_state_position=self.node_names.index(node_name)
            self.current_node=node_name
            self.data=node_data
            self.state=[0 for i in range(len(self.node_names))]
            self.state[current_node_state_position]=1
            self.state_matrix=np.matrix(self.state).T
        except:
            print("Could not set the state of graph: {0}".format(self.graph_name))
            raise

    def add_edge(self,begin_node=None,end_node=None,edge_function=None):
        """Adds an edge mapping one node to another, required input is begin_node (it's name)
        end_node, and the edge function"""
        # check to see if edge is defined if it is increment a number
        edge_match=re.compile("edge_{0}_{1}".format(begin_node,end_node))
        keys=self.__dict__.keys()
        #print keys
        iterator=0
        for key in keys:
            if re.match(edge_match,key):
                iterator+=1
        edge_name="edge_{0}_{1}_{2:0>3d}".format(begin_node,end_node,iterator)
        self.__dict__[edge_name]=edge_function
        self.edges.append(edge_name)
        edge_matrix=np.zeros((len(self.state),len(self.state)))
        begin_position=self.node_names.index(begin_node)
        end_position=self.node_names.index(end_node)
        edge_matrix[end_position][begin_position]=1
        edge_matrix=np.matrix(edge_matrix)
        self.edge_matrices.append(edge_matrix)

    def move_to(self,path):
        """Changes the state of the graph by moving along the path specified"""
        #print path
        for index,edge in enumerate(path):
            #print edge
            edge_pattern='edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)'
            match=re.match(edge_pattern,edge)
            begin_node=match.groupdict()['begin_node']
            end_node=match.groupdict()['end_node']
            print("moving {0} -> {1}".format(begin_node,end_node))
            #print self.data
            self.data=self.__dict__[edge](self.data)
            #print self.data
            self.current_node=match.groupdict()['end_node']
            self.state=[0 for i in range(len(self.node_names))]
            position=self.node_names.index(self.current_node)
            self.state[position]=1
            self.state_matrix=np.matrix(self.state).T
            #print self.state
            #print self.current_node

    def virtual_move_to(self,path):
        """virtual_move_to simulates moving but does not change the state of the graph"""
        #print path
        temp_state=self.state
        temp_data=self.data
        temp_current_node=self.current_node
        temp_node_names=self.node_names
        for index,edge in enumerate(path):
            #print edge
            edge_pattern='edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)'
            match=re.match(edge_pattern,edge)
            begin_node=match.groupdict()['begin_node']
            end_node=match.groupdict()['end_node']
            #print("moving {0} -> {1}".format(begin_node,end_node))
            #print self.data
            temp_data=self.__dict__[edge](temp_data)
            #print self.data
            temp_current_node=match.groupdict()['end_node']
            temp_state=[0 for i in range(len(temp_node_names))]
            position=temp_node_names.index(temp_current_node)
            temp_state[position]=1
            #print temp_state
            #print self.state
            #print self.current_node

    def __str__(self):
        return str(self.data)

    def add_node(self,node_name,edge_into_node_begin,edge_into_node_function,edge_out_node_end,edge_out_node_function):
        """Adds a node to the graph. Required input is node_name (a string with no spaces), a reference to an entering node,
        the function mapping the entering node to the new node, a reference to an exiting node and the function mapping the
        new node to the exiting node."""
        # first check if node into and out of node is good
        self.node_names.append(node_name)
        self.state.append(0)
        self.state_matrix=np.matrix(self.state).T
        for index,matrix in enumerate(self.edge_matrices):
            pad_row=np.zeros((1,len(matrix)))
            new_matrix=np.concatenate((matrix, pad_row), axis=0)
            pad_column=np.zeros((1,len(self.node_names)))
            new_matrix=np.concatenate((new_matrix, pad_column.T), axis=1)
            #print("New matrix is :\n{0}".format(new_matrix))
            self.edge_matrices[index]=new_matrix
        self.add_edge(begin_node=node_name,end_node=edge_out_node_end,edge_function=edge_out_node_function)
        self.add_edge(begin_node=edge_into_node_begin,end_node=node_name,edge_function=edge_into_node_function)

    def path_length(self,path,num_repeats=10):
        """Determines the length of a given path, currently the metric is based on the time to move to."""
        begin_time=datetime.datetime.now()
        #num_repeats=100
        for i in range(num_repeats):
            self.virtual_move_to(path)
        end_time=datetime.datetime.now()
        delta_t=end_time-begin_time
        path_length=delta_t.total_seconds()/float(num_repeats)
        if path_length ==0.0:
            print("Warning the path length is less than 1 microsecond, make sure num_repeats is high enough to measure it.")
        return path_length

    def is_path_valid(self,path):
        """Returns True if the path is valid from the current node position or False otherwise"""
        null_state=[0 for i in range(len(self.node_names))]
        null_state_matrix=np.matrix(null_state).T
        new_state=np.matrix(self.state).T
        for index,edge in enumerate(path):
            #print index
            #print edge
            edge_position=self.edges.index(edge)
            move_matrix=self.edge_matrices[edge_position]
            #print move_matrix
            new_state=move_matrix*new_state
            if new_state.any()==null_state_matrix.any():
                #print new_state
                #print null_state_matrix
                return False
        return True


    def get_entering_nodes(self,node):
        """Returns all nodes that have an edge that enter the specificed node"""
        enter_edge_pattern=re.compile('edge_(?P<begin_node>\w+)_{0}_(?P<iterator>\w+)'.format(node))
        enter_nodes=[]
        for index,edge in enumerate(self.edges):
            enter_match=re.match(enter_edge_pattern,edge)
            if enter_match:
                enter_node=enter_match.groupdict()['begin_node']
                enter_nodes.append(enter_node)
        return enter_nodes

    def get_entering_edges(self,node):
        """Returns all edges that enter the specificed node"""
        enter_edge_pattern=re.compile('edge_(?P<begin_node>\w+)_{0}_(?P<iterator>\w+)'.format(node))
        enter_edges=[]
        for index,edge in enumerate(self.edges):
            if re.match(enter_edge_pattern,edge):
                enter_edges.append(edge)
        return enter_edges

    def get_exiting_edges(self,node):
        """Returns all edges that exit the specificed node"""
        exit_edge_pattern=re.compile('edge_{0}_(?P<end_node>\w+)_(?P<iterator>\w+)'.format(node))
        exit_edges=[]
        for index,edge in enumerate(self.edges):
            if re.match(exit_edge_pattern,edge):
                exit_edges.append(edge)
        return exit_edges

    def get_exiting_nodes(self,node):
        """Returns all nodes that have an edge leaving the specificed node"""
        exit_edge_pattern=re.compile('edge_{0}_(?P<end_node>\w+)_(?P<iterator>\w+)'.format(node))
        exit_nodes=[]
        for index,edge in enumerate(self.edges):
            exit_match=re.match(exit_edge_pattern,edge)
            if exit_match:
                exit_node=exit_match.groupdict()['end_node']
                exit_nodes.append(exit_node)
        return exit_nodes

    def get_path(self,first_node,last_node):
        """Returns the first path found between first node and last node"""
        edge_pattern=re.compile('edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)')
        exit_paths=self.get_exiting_edges(first_node)
        next_nodes=self.get_exiting_nodes(first_node)
        #be careful here using the wrong assignment statement breaks this function
        possible_paths=[]
        for exit_path in exit_paths:
            possible_paths.append([exit_path])
        #print("{0} is {1}".format('possible_paths',possible_paths))
        for i in range(len(self.node_names)):
            for index,path in enumerate(possible_paths):
                last_edge=path[-1]
                match=re.match(edge_pattern,last_edge)
                begin_node=match.groupdict()['begin_node']
                end_node=match.groupdict()['end_node']
                #print next_node
                if end_node==last_node:
                    #print("The path found is {0}".format(path))
                    return path
                next_possible_paths=[]
                next_edges=self.get_exiting_edges(end_node)
                next_nodes=self.get_exiting_nodes(end_node)
                #print("{0} is {1}".format('next_edges',next_edges))
                for index,next_edge in enumerate(next_edges):
                    #be careful here using the wrong assignment statement breaks this function
                    #next_path=path is a deal breaker!!
                    next_path=[]
                    for edge in path:
                        next_path.append(edge)
                    #print("{0} is {1}".format('next_path',next_path))
                    #print("{0} is {1}".format('next_edge',next_edge))
                    #next_node=next_nodes[index]
                    #print next_node
                    next_match=re.match(edge_pattern,next_edge)
                    next_node=next_match.groupdict()["end_node"]
                    begin_node_next_edge=next_match.groupdict()["begin_node"]
                    #print("{0} is {1}".format('next_node',next_node))
                    #print("{0} is {1}".format('begin_node_next_edge',begin_node_next_edge))

                    if next_node==last_node and begin_node_next_edge==end_node:
                        next_path.append(next_edge)
                        #print("The path found is {0}".format(next_path))
                        return next_path
                    elif begin_node_next_edge==end_node:
                        next_path.append(next_edge)
                        next_possible_paths.append(next_path)
                        #print("{0} is {1}".format('next_possible_paths',next_possible_paths))
                    else:
                        pass
                    #print("{0} is {1}".format('next_possible_paths',next_possible_paths))
                possible_paths=next_possible_paths
                #print("{0} is {1}".format('possible_paths',possible_paths))

    def move_to_node(self,node):
        """Moves from current_node to the specified node"""
        path=self.get_path(self.current_node,node)
        self.move_to(path)

    def check_closed_path(self):
        """Checks that data is not changed for the first closed path found. Returns True if data==data after
        moving around the closed path, False otherwise. Starting point is current_node """
        temp_data=self.data
        path=self.get_path(self.current_node,self.current_node)
        if self.is_path_valid(path):
            pass
        else:
            print("Path is not valid, graph definition is broken")
            raise
        out=temp_data==self.data
        out_list=[self.current_node,path,out]
        print("The assertion that the data remains unchanged,\n"
              "for node {0} following path {1} is {2}".format(*out_list))
        return out

    def is_graph_isomorphic(self):
        """Returns True if all nodes have closed paths that preserve the data, False otherwise"""
        out=True
        for node in self.node_names:
            self.move_to_node(node)
            if not self.check_closed_path:
                out=False
        return out

class StringGraph(Graph):
    """String Graph is  a graph relating different string forms"""
    def __init__(self,**options):
        """Intializes the StringGraph Class by defining nodes and edges"""
        defaults={"graph_name":"StringGraph",
                  "node_names":['n1','n2'],
                  "node_descriptions":{'n1':"A plain string",
                                       'n2':"A list of strings with no \\n, created with string.splitlines()"},
                  "current_node":'n1',
                  "state":[1,0],
                  "data":"This is a test string\n it has to have multiple lines \n and many characters 34%6\n^",
                  "edge_2_to_1":edge_2_to_1,
                  "edge_1_to_2":edge_1_to_2
                 }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        Graph.__init__(self,**self.options)
#-----------------------------------------------------------------------------
# Module Scripts
#TODO: Add test_Graph script currently lives in jupyter-notebooks
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass