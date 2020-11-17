

#basics
from pprint import pprint
from copy import deepcopy
import numpy as np
import random

#igraph
import igraph
from igraph import Graph, EdgeSeq

#plotly
import plotly.express as px
import plotly.graph_objects as go


def normalize_row_coordinates(plot_data):
    Y = np.array(plot_data["Y"])
    X = np.array(plot_data["X"], dtype=float)

    # where level is == 1, this is the level of all trees
    tree_level_mask = Y==1
    new_xs = X[tree_level_mask] * ( plot_data["max_width"] /  len(plot_data["tree_widths"]))
    X[tree_level_mask] = new_xs
    plot_data["X"] = X.tolist()

    ## TODO:
    # we need to shift the subtrees of the main tree to make them look a bit nicer
    #
    # possible solutions:
    # shift each level for each tree according to :
    #
    #

    # for tree in trees:
    #     for i in range(2,plot_data["max_depth"]+1):
    #         level_mask = Y == i
    #         tree_maks = root == tree
    #         mask  = level_mask + level_mask
    #         new_xs = X[mask]
    #         new_xs = new_xs * ( plot_data["max_width"]  ( plot_data["tree_widths"][tree] / len(new_xs) )
    #         X[level_mask] = new_xs
    #         plot_data["X"] = X.tolist()


def set_link_coordinates(plot_data, labels:list, colors:list):

    for label in labels:
        plot_data["link_xy"][label] = {
                                        "X":[],
                                        "Y": [],
                                        "style": dict(color=colors.pop(0), width=2, dash='solid')
                                        }
        
    for link_label, idx_of_parent, idx_of_child in plot_data["links"]:
        plot_data["link_xy"][link_label]["X"].extend([plot_data["X"][idx_of_parent], plot_data["X"][idx_of_child], None])
        plot_data["link_xy"][link_label]["Y"].extend([plot_data["Y"][idx_of_parent], plot_data["Y"][idx_of_child], None])


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
                "link_xy": {}
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
        
            plot_data["level_widths"][row] += 1

            found = True
        else:
            found = place_node(trees, node, linked_node, link_label, plot_data)
    

        # if node found a place we remove it else we just add it
        # last to the unplaced_nodes list
        #node_tuple = unplaced_nodes.pop(0)
        if not found and (node, linked_node, link_label) not in unplaced_nodes:
            unplaced_nodes.append((node, linked_node, link_label))

    plot_data["max_width"] =  max(plot_data["level_widths"].values())
    return plot_data


def add_node_text(fig, plot_data):
    annotations = [dict(
                                text=l, 
                                x=plot_data["X"][i], 
                                y=plot_data["Y"][i],
                                xref='x1', yref='y1',
                                font=dict(color='black', size=10),
                                showarrow=False
                                ) 
                    for i, l in enumerate(plot_data["labels"])]

    fig.update_layout(
                        annotations=annotations,
                        )


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


def add_lines(fig, plot_data):
    for label, link_data in plot_data["link_xy"].items():
        fig.add_trace(go.Scatter(
                                x=link_data["X"],
                                y=link_data["Y"],
                                mode='lines',
                                name=label,
                                line=link_data["style"],
                                #text = ,
                                hoverinfo="none",
                                ))


def add_nodes(fig, plot_data, texts, colors:list):
    fig.add_trace(go.Scatter(
                            x=plot_data["X"],
                            y=plot_data["Y"],
                            mode='markers',
                            name='bla',
                            marker=dict(symbol='diamond-wide',
                                            size=50,
                                            color=colors.pop(0),
                                            #opacity=0.0,
                                            ),
                            text=plot_data["labels"],
                            hovertext=texts,
                            hoverinfo='text',
                            showlegend=False,
                            #opacity=0.8
                            ))


def set_axes(fig, plot_data, reverse:bool):
    fig.update_layout(
                    yaxis=dict(range=[0,plot_data["max_depth"]+1], autorange="reversed" if reverse else None),
                    xaxis=dict(range=[0,plot_data["max_width"]+1])
                    )

def format_text(texts):
    # simply divides a text into lines with max 10 words
    new_texts = []
    for text in texts:
        tokens  = text.split(" ")
        new_texts.append("<br>".join([" ".join(tokens[i:i+10]) for i in range(0,len(tokens),10)]))
    return new_texts


def create_tree_plot(fig, data:dict, colors:str, reverse:bool): # nodes:list, links:list, color:str):

    #we turn labels into ids
    data["node_ids"] = create_ids(data["nodes"])

    # change links to label ids by taking the label id of the idx == link
    data["linked_nodes"] = [data["node_ids"][i] for i in data["links"]]

    # sort data to untangle trees
    sorted_data = sort_data(data)

    #unpack
    node_ids = sorted_data.get("node_ids")
    linked_nodes = sorted_data.get("linked_nodes")
    link_labels = sorted_data.get("link_labels", [""] * len(node_ids))
    texts = sorted_data.get("texts")
    texts = format_text(texts)

    # zip node labels, linked node labels and link_labels
    node_tuples = list(zip(node_ids,linked_nodes, link_labels))

    # parse the data to get plot data ( e.g. X Y coordinates, max depth, max width etc)
    plot_data = get_plot_data(node_tuples)

    #normalize coordinates to make tree abit nicer now as we know the depth and widths
    normalize_row_coordinates(plot_data)

    # when we have normalized X and Y corridnates we can set up all the links
    set_link_coordinates(plot_data, labels=sorted(set(link_labels)), colors=colors)
    
    #create the plot
    add_lines(fig, plot_data)
    add_nodes(fig, plot_data, texts, colors=colors)
    add_node_text(fig, plot_data)
    set_axes(fig, plot_data, reverse=reverse)


def hot_tree(gold, pred=None, colors="Plotly", reverse=True):

    fig = go.Figure()

    #get colors scale
    for scale in [px.colors.sequential, px.colors.qualitative, px.colors.cyclical]:
        if hasattr(scale, colors):
            colors = getattr(scale ,colors)
            break
            
    if type(colors) != list:
        raise KeyError(f"{colors} is not a supported plotly colorscale. scales can be found here: https://plotly.com/python/builtin-colorscales/")
    
    #creating gold tree
    create_tree_plot(fig, 
                    data=gold,
                    colors=colors,
                    reverse=reverse,
                    )

    if pred:
        create_tree_plot(fig, 
                        nodes=pred["nodes"], 
                        links=pred["links"], 
                        color="green"
                        )

    fig.update_layout(
                        title= 'Argument Tree',
                        #annotations=make_annotations(name2pos),
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