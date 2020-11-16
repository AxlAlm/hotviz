
import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
from pprint import pprint
import time
from copy import deepcopy
import numpy as np


def normalize_row_coordinates(plot_data):
    Y = np.array(plot_data["Y"])
    X = np.array(plot_data["X"], dtype=float)

    # where level is == 1, this is the level of all trees
    tree_level_mask = Y==1
    new_xs = X[tree_level_mask] * ( plot_data["max_width"] /  len(plot_data["tree_widths"]))
    X[tree_level_mask] = new_xs
    plot_data["X"] = X.tolist()

    for i in range(1,plot_data["max_depth"]+1):
        print(i)


def set_link_coordinates(plot_data):
    plot_data.update({
                    "Ylink": [],
                    "Xlink": []
                    })
    for link_type, idx_of_parent, idx_of_child in plot_data["links"]:
        plot_data["Xlink"].extend([plot_data["X"][idx_of_parent], plot_data["X"][idx_of_child], None])
        plot_data["Ylink"].extend([plot_data["Y"][idx_of_parent], plot_data["Y"][idx_of_child], None])


def create_trees(items):
    """
        For each node we look for its link in other nodes, if link exists we add node as subtree to the
        linked node.
        We set column and row as following:
        column = nr of nodes on current row + 1
        row = row of parent + 1
        

        First we figure out the positions accross X (column) and Y (row) for each  node in the tree.

        Then to make the tree a little bit nicer we normalize the X,Y by the max widths and tree widths

        When we have the new coordinates we can create a list of X,Y coordinates that will be used
        to link the nodes, these arrays are Xlink and Ylink



        NOTE! we will later update the columns given the width of each tree.
        So, we create a mask for selecting the parts we might need to confiugre later
        a) tree
        b) tree rows 
        c) root nodes
        
        when we have the order of the column and rows and max width
        we can apply the following calculations to fix all coordinates
        
        a = max(number rows on all levels)
        c = biggest_row
        for each row:
          if row > biggest row:
              new_columns_coordiantes
          else:
              space = a / nr nodes on row
              new_columns_coordiantes = [i*space for i in row_positions]
        
    """
    
    def place_node(tree_nodes, node, linked_node, plot_data):


        if linked_node in tree_nodes:
            parent_node = tree_nodes[linked_node]
            root = parent_node["root"]

            row = parent_node["row"] + 1

            if row not in plot_data["level_widths"]:
                plot_data["level_widths"][row] = 0
            
            plot_data["level_widths"][row] += 1
            column = plot_data["level_widths"][row]

            idx = len(plot_data["X"])
            plot_data["X"].append(column)
            plot_data["Y"].append(row)
            plot_data["root"].append(root)
            plot_data["links"].append(("LINK TYPE", parent_node["idx"], idx))
            plot_data["labels"].append(node)
            plot_data["max_depth"] = max(plot_data["max_depth"], row)

            parent_node["subnodes"][node] =  {
                                                "row":row,        
                                                "column":column,
                                                "root":root,
                                                "idx": idx,
                                                "subnodes":{}
                                                }
            
            # we need to know the width of a tree so we can normalzie the coordinates later
            plot_data["tree_widths"][root] = max(plot_data["tree_widths"][root], len(parent_node["subnodes"]))
            return True
        else:
            for node_id, node_dict in tree_nodes.items():
                if place_node(node_dict["subnodes"], node, linked_node, plot_data):
                    return True
                    
            return False

    plot_data = {
                "X":[],
                "Y":[], 
                #"Xlink":[], 
                #"Ylink":[],
                "links": [],
                "labels": [],
                "root":[], 
                "max_depth":0, 
                "tree_widths":{},
                "level_widths":{},
                }
    trees = {}

    unplaced_nodes = items.copy()
    while unplaced_nodes:

        #node, linked_node = unplaced_nodes[0]
        node, linked_node  = unplaced_nodes.pop(0)

        #if we have a node that points to itself its the root of a new tree
        if node == linked_node:
            row = 1
            column = len(trees)+1
            idx = len(plot_data["X"])
            trees[node] = {
                            "row":row,        
                            "column":column,
                            "root":node,
                            "idx": idx,
                            "subnodes":{}
                            }
            plot_data["X"].append(column)
            plot_data["Y"].append(row)
            plot_data["root"].append(node)
            plot_data["labels"].append(node)
            plot_data["tree_widths"][node] = 1

            if row not in plot_data["level_widths"]:
                plot_data["level_widths"][row] = 0
        
            else:
                plot_data["level_widths"][row] += 1

            found = True
        else:
            found = place_node(trees, node, linked_node, plot_data)
    

        # if node found a place we remove it else we just add it
        # last to the unplaced_nodes list
        #node_tuple = unplaced_nodes.pop(0)
        if not found and (node, linked_node) not in unplaced_nodes:
            unplaced_nodes.append((node, linked_node) )

    plot_data["max_width"] =  sum(plot_data["tree_widths"].values())

    #pprint(trees)
    #pprint(plot_data)
    normalize_row_coordinates(plot_data)
    set_link_coordinates(plot_data)

    return plot_data



def parse_tree(
                tree, 
                max_depth=None,
                max_width=None,
                # start_column:int,
                # end_column: int,
                # row: int,
                link_to_x=None,
                link_to_y=None,
               ):
    
    """
    given a tree structured dict we traverse the tree and create coordinates for 
    links and for nodes.

    X and Y are for nodes
    
    Xlink and Ylink are for linkes. Each X,y coordinate is followed by None to WHAHAHHAHT

    """
    # row_level = row
    # column_level = start_column 
    
    X = []
    Y = []
    Xlink = []
    Ylink = []
    labels = []
    prev_tree_width = 0
    #colum_step = (end_column-start_column) / len(tree["subtree"].items())

    for name, subtree in tree["subtree"].items():
        
        # # if the tree is a root tree
        if subtree["root"] == name:
            max_width = subtree["width"] + prev_tree_width +1
            start_column = prev_tree_width +1
            prev_tree_width = max_width 

        # + prev_tree_width

        #max_depth = subtree["depth"]

        #     # print(name, subtree)
        #     # width = subtree["width"]
        #     # depth = subtree["depth"]
        #     position = subtree["position"]

        #     c = max_width / 2
        #     r = max_depth
        #     prev_tree_width =+ max_width
        # else:
        
        c = (max_width+1) - subtree["position"]
        r = (max_depth - subtree["depth"]) 

        print(name, subtree)
        print(name, c, r)

        X.append(c) #column_level)
        Y.append(r) #row_level) 
        labels.append(name)

        Xlink.extend([link_to_x, c, None])
        Ylink.extend([link_to_y, r, None])
        
        if subtree["subtree"]:
            #half_step = colum_step #/2
            xx,yy, xl, yl, ll = parse_tree(
                                            subtree,
                                            max_depth=max_depth,
                                            max_width=max_width,
                                            #start_column= ,#column_level-half_step,
                                            #end_column= ,#column_level+half_step,
                                            #row=row-1,
                                            link_to_x=c,
                                            link_to_y=r
                                            )
            X.extend(xx)
            Y.extend(yy)
            Xlink.extend(xl)
            Ylink.extend(yl)
            labels.extend(ll)
            

        #column_level += colum_step

    return X, Y, Xlink, Ylink, labels


def make_annotations(name2pos):
    """
    creates a dict over the position of annotations for nodes
    """
    annotations = []
    for name,pos in name2pos.items():
        annotations.append(
                            dict(
                                text=name, # or replace labels with a different list for the text within the circle
                                x=pos[0], y=pos[1],
                                xref='x1', yref='y1',
                                font=dict(color='black', size=10),
                                showarrow=False
                                )
                        )
    return annotations


def create_ids(nodes):
    node_stack = {}
    nodes_ids = []
    for node in nodes:
        
        if node not in node_stack:
            node_stack[node] = []
        
        node_id = f"{node}_{len(node_stack[node])}"
        
        node_stack[node].append(node)
        nodes_ids.append(node_id)

    return nodes_ids


def sort_data(data):
    data = deepcopy(data)
    links = data.pop("links")
    data_keys = list(data.keys())
    sorted_values = list(zip(*sorted(zip(*data.values(),links), key=lambda x:x[-1])))
    sorted_data = {}
    for i, k in enumerate(data_keys):
        sorted_data[k] = sorted_values[i]
    return sorted_data

def create_tree_plot(fig, data:dict, color:str, group:str): # nodes:list, links:list, color:str):

    data["node_ids"] = create_ids(data["nodes"])
    data["linked_nodes"] = [data["node_ids"][i] for i in data["links"]]

    sorted_data = sort_data(data)

    node_ids = sorted_data.get("node_ids")
    linked_nodes = sorted_data.get("linked_nodes")
    link_labels = sorted_data.get("link_labels")
    texts = sorted_data.get("texts")

    node_tuples = list(zip(node_ids,linked_nodes))
    plot_data = create_trees(node_tuples)
    
    X = plot_data["X"]
    Y = plot_data["Y"]
    Xlink = plot_data["Xlink"]
    Ylink = plot_data["Ylink"]
    labels = plot_data["labels"]

    max_depth = plot_data["max_depth"] + 1
    max_width = plot_data["max_width"] + 1

    name2pos = {}
    for i,l in enumerate(labels):
        name2pos[l] = (X[i],Y[i])
    
    
    fig.add_trace(go.Scatter(
                            x=X,
                            y=Y,
                            mode='markers',
                            name='bla',
                            marker=dict(symbol='diamond-wide',
                                            size=50,
                                            color=color,
                                            #opacity=0.0,
                                            ),
                            text=labels,
                            hovertext=texts,
                            hoverinfo='text',
                            legendgroup=group,
                            #opacity=0.8
                            ))

    fig.update_layout(
                    yaxis=dict(range=[0,max_depth]),
                    xaxis=dict(range=[0,max_width])
                    )

    fig.add_trace(go.Scatter(
                            x=Xlink,
                            y=Ylink,
                            mode='lines',
                            name="True",
                            line=dict(color=color, width=1),
                            hoverinfo='none',
                            legendgroup=group,

                            ))

    fig.update_layout(
                        annotations=make_annotations(name2pos),
                        )
    
    return name2pos


def hot_tree(gold, pred=None):


    fig = go.Figure()

    #creating gold tree
    name2pos = create_tree_plot(fig, 
                                data=gold,
                                color="LightBlue",
                                group="gold"
                                )


    if pred:
        create_tree_plot(fig, 
                        nodes=pred["nodes"], 
                        links=pred["links"], 
                        color="green"
                        )

    fig.update_layout(
                        title= 'Argument Tree',
                        annotations=make_annotations(name2pos),
                        font_size=12,
                        showlegend=True,
                        margin=dict(l=40, r=40, b=85, t=100),
                        hovermode='closest',
                        plot_bgcolor='rgb(248,248,248)'
                        )

    axis = dict(
                showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
            )

    return fig