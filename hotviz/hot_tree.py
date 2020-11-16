
import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
from pprint import pprint
import time
from copy import deepcopy
import numpy as np
import random



def normalize_row_coordinates(plot_data):
    Y = np.array(plot_data["Y"])
    X = np.array(plot_data["X"], dtype=float)

    # where level is == 1, this is the level of all trees
    tree_level_mask = Y==1
    new_xs = X[tree_level_mask] * ( plot_data["max_width"] /  len(plot_data["tree_widths"]))
    X[tree_level_mask] = new_xs
    plot_data["X"] = X.tolist()

    # for tree in trees:
    #     for i in range(2,plot_data["max_depth"]+1):
    #         level_mask = Y == i
    #         tree_maks = root == tree
    #         mask  = level_mask + level_mask
    #         new_xs = X[mask]
    #         new_xs = new_xs * ( plot_data["max_width"]  ( plot_data["tree_widths"][tree] / len(new_xs) )
    #         X[level_mask] = new_xs
    #         plot_data["X"] = X.tolist()


def set_link_coordinates(plot_data, nr_styles):

    colors = [ "green", "red", "blue", "black"] #"lightblue", "orange",
    line_styles = [dict(color=colors[i], width=2, dash='dash') for i in range(nr_styles)]
    i = 0
    for link_label, idx_of_parent, idx_of_child in plot_data["links"]:
        
        if link_label:
            ykey = f"Y{link_label}link"
            xkey = f"X{link_label}link"
        else:
            ykey = "Ylink"
            xkey = "Xlink"

        if link_label not in plot_data["link_styles"]:
            plot_data[ykey] = []
            plot_data[xkey] = []
            plot_data["link_styles"][link_label] = line_styles[i]
            i += 1

        plot_data[xkey].extend([plot_data["X"][idx_of_parent], plot_data["X"][idx_of_child], None])
        plot_data[ykey].extend([plot_data["Y"][idx_of_parent], plot_data["Y"][idx_of_child], None])


def get_plot_data(items):

    def place_node(tree_nodes, node, linked_node, link_label, plot_data):


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
            plot_data["links"].append((link_label, parent_node["idx"], idx))
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
                if place_node(node_dict["subnodes"], node, linked_node, link_label, plot_data):
                    return True
                    
            return False

    plot_data = {
                "X":[],
                "Y":[], 
                "links": [],
                "labels": [],
                "root":[], 
                "max_depth":0, 
                "tree_widths":{},
                "level_widths":{},
                "link_styles": {}
                #"start_x": 0,
                #"start_y": 0,
                }
    trees = {}

    unplaced_nodes = items.copy()
    while unplaced_nodes:

        #node, linked_node = unplaced_nodes[0]
        node, linked_node, link_label  = unplaced_nodes.pop(0)

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
            found = place_node(trees, node, linked_node, link_label, plot_data)
    

        # if node found a place we remove it else we just add it
        # last to the unplaced_nodes list
        #node_tuple = unplaced_nodes.pop(0)
        if not found and (node, linked_node) not in unplaced_nodes:
            unplaced_nodes.append((node, linked_node) )

    plot_data["max_width"] =  sum(plot_data["tree_widths"].values())

    return plot_data


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


def create_tree_plot(fig, data:dict, color:str, group:str, reverse=True): # nodes:list, links:list, color:str):

    data["node_ids"] = create_ids(data["nodes"])
    data["linked_nodes"] = [data["node_ids"][i] for i in data["links"]]

    sorted_data = sort_data(data)

    node_ids = sorted_data.get("node_ids")
    linked_nodes = sorted_data.get("linked_nodes")
    link_labels = sorted_data.get("link_labels", [""] * len(node_ids))
    texts = sorted_data.get("texts")


    node_tuples = list(zip(node_ids,linked_nodes, link_labels))
    plot_data = get_plot_data(node_tuples)

    normalize_row_coordinates(plot_data)
    set_link_coordinates(plot_data, nr_styles=len(set(link_labels)))
    
    X = plot_data["X"]
    Y = plot_data["Y"]
    labels = plot_data["labels"]

    max_depth = plot_data["max_depth"] + 1
    max_width = plot_data["max_width"] + 1

    name2pos = {}
    for i,l in enumerate(labels):
        name2pos[l] = (X[i],Y[i])
    
    for link_label, style in plot_data["link_styles"].items():
        xkey = f"X{link_label}link"
        ykey = f"Y{link_label}link"

        fig.add_trace(go.Scatter(
                                x=plot_data[xkey],
                                y=plot_data[ykey],
                                mode='lines',
                                name=link_label,
                                line=style,
                                #text = ,
                                hoverinfo="none",
                                legendgroup=group,
                                ))

    
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
                    yaxis=dict(range=[0,max_depth], autorange="reversed" if reverse else None),
                    xaxis=dict(range=[0,max_width])
                    )

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