

#basics
from copy import deepcopy
import numpy as np
import random

#igraph
import igraph
from igraph import Graph, EdgeSeq

#plotly
import plotly.express as px
import plotly.graph_objects as go

import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib as mpl

def get_color_hex(cmap_name:str, value=1.0):
    norm = mpl.colors.Normalize(vmin=0.0,vmax=2)
    cmap = cm.get_cmap(cmap_name)
    hex_code = colors.to_hex(cmap(norm(value)))
    return hex_code


def normalize_row_coordinates(plot_data):
    Y = np.array(plot_data["Y"])
    X = np.array(plot_data["X"], dtype=float)

    # where level is == 1, this is the level of all trees
    # first part only alines the trees so they are equally distributed over the max width
    tree_level_mask = Y==1
    
    max_width = plot_data["max_width"]
    max_depth = plot_data["max_depth"]
    nr_trees = len(plot_data["tree_widths"])
    if nr_trees == 1:
        nr_trees += 1

    new_xs = X[tree_level_mask] * ( max_width /   nr_trees)
    X[tree_level_mask] = new_xs
    plot_data["X"] = X.tolist()

    for level in range(2, max_depth):
        level_width = plot_data["level_widths"][level]
        tree_level_mask = Y == level
        new_xs = X[tree_level_mask] * ( max_width /   level_width)
        X[tree_level_mask] = new_xs
        plot_data["X"] = X.tolist()


def set_link_coordinates(plot_data, labels:list):

    for label in labels:
        plot_data["link_xy"][label] = {
                                        "X":[],
                                        "Y": [],
                                        }
        
    for link_label, idx_of_parent, idx_of_child in plot_data["links"]:
        plot_data["link_xy"][link_label]["X"].extend([plot_data["X"][idx_of_parent], plot_data["X"][idx_of_child], None])
        plot_data["link_xy"][link_label]["Y"].extend([plot_data["Y"][idx_of_parent], plot_data["Y"][idx_of_child], None])


def get_plot_data(data):

    def place_node(tree_nodes, node, plot_data):
        if node["link"] in tree_nodes:
            parent_node = tree_nodes[node["link"]]
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
            plot_data["links"].append((node["link_label"], parent_node["idx"], idx))
            plot_data["ids"].append(node["id"])
            plot_data["labels"].append(node["label"])
            plot_data["max_depth"] = max(plot_data["max_depth"], row)
            plot_data["texts"].append(format_text(node["text"]))
            parent_node["subnodes"][node["id"]] =  {
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
                if place_node(node_dict["subnodes"], node, plot_data):
                    return True
                    
            return False

    plot_data = {
                "X":[],
                "Y":[], 
                "links": [],
                "labels": [],
                "ids": [],
                "texts": [],
                "root":[], 
                "max_depth":0, 
                "tree_widths":{},
                "level_widths":{},
                "link_xy": {}
                }
    trees = {}

    # addin "seen" (and copy)
    unplaced_nodes = [{**node,**{"seen":0}} for node in data.copy()]
    while unplaced_nodes:

        node  = unplaced_nodes.pop(0)

        #if we have a node that points to itself its the root of a new tree
        if node["id"] == node["link"]:
            row = 1
            column = len(trees)+1
            idx = len(plot_data["X"])
            trees[node["id"]] = {
                            "row":row,        
                            "column":column,
                            "root":node["id"],
                            "idx": idx,
                            "subnodes":{}
                            }
            plot_data["X"].append(column)
            plot_data["Y"].append(row)
            plot_data["labels"].append(node["label"])
            plot_data["root"].append(node["id"])
            plot_data["ids"].append(node["id"])
            plot_data["tree_widths"][node["id"]] = 1
            plot_data["texts"].append(format_text(node["text"]))

            if row not in plot_data["level_widths"]:
                plot_data["level_widths"][row] = 0
        
            plot_data["level_widths"][row] += 1

            found = True
        else:
            found = place_node(trees, node, plot_data)
    
        # if node found a place we remove it else we just add it
        # last to the unplaced_nodes list
        if not found and node not in unplaced_nodes:

            if node["seen"] >= 2:
                row = 1
                column = len(trees)+1
                idx = len(plot_data["X"])
                trees[node["id"]] = {
                                "row":row,        
                                "column":column,
                                "root":node["id"],
                                "idx": idx,
                                "subnodes":{}
                                }      
                plot_data["X"].append(column)
                plot_data["Y"].append(row)
                plot_data["root"].append(node["id"])
                plot_data["labels"].append(node["id"])
                plot_data["tree_widths"][node["id"]] = 1
                plot_data["texts"].append(format_text(node["text"]))

                if row not in plot_data["level_widths"]:
                    plot_data["level_widths"][row] = 0
            
                plot_data["level_widths"][row] += 1

            else:
                node["seen"] += 1
                unplaced_nodes.append(node)

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
                    for i, l in enumerate(plot_data["ids"])]

    fig.update_layout(
                        annotations=annotations,
                        )


def replacement_legend(fig, legendgroup:str):
    fig.add_trace(go.Scatter(
                            x=[0],
                            y=[0],
                            visible=True,
                            mode="markers",
                            marker=dict(symbol='square',
                                        size=50,
                                        color="white"
                                        ),
                            name=legendgroup,
                            showlegend=True,
                            legendgroup=legendgroup,
                            ))
    fig.update_layout(
                        legend= dict(
                                    font=dict(
                                                family="Courier",
                                                size=15,
                                                color="black"
                                             )
                                    )
                        )
    

def add_lines(fig, plot_data, opacity:float, legendgroup:str, link_label2color:dict):
    for label, link_data in plot_data["link_xy"].items():

        legend = f"{legendgroup}-{label}"
        style = dict(
                    color=link_label2color[label], 
                    width=2, 
                    dash='solid'
                    )

        fig.add_trace(go.Scatter(
                                x=link_data["X"],
                                y=link_data["Y"],
                                mode='lines',
                                name=label,
                                line=style,
                                hoverinfo="none",
                                showlegend=True,
                                legendgroup=legendgroup,
                                opacity=opacity,
                                ))


def add_nodes(fig, plot_data, opacity:float, legendgroup:str, node_size:int, label2color:dict):


    groups = {l:{"X":[],"Y":[], "texts":[], "ids":[]} for l in label2color.keys()}
    for x,y, text, ID, label in zip(plot_data["X"], plot_data["Y"], plot_data["texts"], plot_data["ids"], plot_data["labels"]):
        groups[label]["X"].append(x)
        groups[label]["Y"].append(y)
        groups[label]["ids"].append(ID)
        groups[label]["texts"].append(text)

    for label, plot_data in groups.items():
        legend = f"{legendgroup}-{label}"
        fig.add_trace(go.Scatter(
                                x=plot_data["X"],
                                y=plot_data["Y"],
                                mode='markers+text',
                                name=label,
                                legendgroup=legendgroup,
                                showlegend=True,
                                marker=dict(    
                                                #symbol='diamond-wide',
                                                symbol='circle',
                                                size=node_size,
                                                color=label2color[label],
                                                #opacity=colors,
                                                ),
                                text=plot_data["ids"],
                                hovertext=plot_data["texts"],
                                hoverinfo='text',
                                opacity=opacity,
                                textposition='middle center'
                                
                                ))


def format_text(text:str):
    tokens = text.split(" ")
    return "<br>".join([" ".join(tokens[i:i+10]) for i in range(0,len(tokens),10)])


def convert_links_ids(data):
    """
    changes link from int to string id
    """
    id2idx = {d["id"]:i for i,d in enumerate(data)}

    for node in data:
        link  = node["link"]

        if isinstance(link, int):
            node["link_int"] = link
            node["link"] = data[link]["id"]
        else:
            node["link_int"] = id2idx[link]


def create_ids(data):
    node_stack = {}
    for node in data:
        label = node["label"]

        if label not in node_stack:
            node_stack[label] = []
        
        node_id = f"{label}_{len(node_stack[label])}"
        
        node_stack[label].append(label)
        node["id"] = node_id


def create_tree_plot(fig, 
                    data:dict,
                    label2color:dict,
                    link_label2color:dict,                      
                    reverse:bool, 
                    opacity:float=1.0, 
                    legendgroup:str=None, 
                    node_size:int=90
                    ): # nodes:list, links:list, color:str):

    data = deepcopy(data)

    #we turn labels into ids
    if "id" not in data[0]:
        create_ids(data)

    # change links
    convert_links_ids(data)

    # sort data to untangle trees
    data = sorted(data, key=lambda x:x["link_int"])

    # parse the data to get plot data ( e.g. X Y coordinates, max depth, max width etc)
    plot_data = get_plot_data(data)

    #normalize coordinates to make tree abit nicer now as we know the depth and widths
    normalize_row_coordinates(plot_data)

    # when we have normalized X and Y corridnates we can set up all the links
    link_labels = list(link_label2color.keys())
    set_link_coordinates(plot_data, labels=link_labels)
    
    #create the plot
    add_lines(fig, plot_data, opacity=opacity, legendgroup=legendgroup, link_label2color=link_label2color)
    add_nodes(fig, plot_data, opacity=opacity, legendgroup=legendgroup, node_size=node_size, label2color=label2color)
    #add_node_text(fig, plot_data)
    
    return plot_data["max_depth"], plot_data["max_width"]


def get_colors(data, gold_data, labels, link_labels, label2color, link_label2color):


    if not labels:
        labels = set([d["label"] for d in data])

        if gold_data:
            labels.update([d["label"] for d in gold_data])
        
        labels = sorted(labels)

    if not link_labels:
        
        link_labels = set([d["link_label"] for d in data])

        if gold_data:
            link_labels.update([d["link_label"] for d in gold_data])

        link_labels = sorted(link_labels)

    if labels and not label2color:
        lc = ["#5ac18e", "#7fe5f0", "#ffa500", "#008080", "#ff4040", "#8a2be2", "#b6fcd5", "#b4eeb4", "#ff7f50"]
        label2color = {l:lc[i] for i,l in enumerate(labels)}

    if link_labels and not link_label2color:
        rc = ["#e43518", "#25c130", "#7c1dbb", "#998002", "#0f34d4", "#f58a00"]

        link_label2color = {r:rc[i] for i,r in enumerate(link_labels)}

    return label2color, link_label2color


def hot_tree(
            data, 
            gold_data=None, 
            labels:list=None, 
            link_labels:list=None, 
            reverse:bool=True, 
            title:str="", 
            save_to:str=None, 
            node_size=90,
            label2color:dict=None,
            link_label2color:dict=None,
            ):

    label2color, link_label2color = get_colors(data, gold_data, labels, link_labels, label2color, link_label2color)

    fig = go.Figure()   

    # gold data is added , we can create a tree with high opacity that just sits static in the background
    if gold_data:
        replacement_legend(fig, "gold")
        gold_max_depth, gold_max_width = create_tree_plot(  
                                                            fig, 
                                                            data=gold_data,
                                                            label2color=label2color,
                                                            link_label2color=link_label2color,
                                                            reverse=reverse,
                                                            opacity=0.3,
                                                            legendgroup="gold",
                                                            node_size=node_size
                                                            )

    legendgroup = None
    if gold_data:
        replacement_legend(fig, "pred")
        legendgroup = "pred"
    
    max_depth, max_width = create_tree_plot(  
                                            fig, 
                                            data=data,
                                            label2color=label2color,
                                            link_label2color=link_label2color,                                            
                                            reverse=reverse,
                                            legendgroup=legendgroup,
                                            node_size=node_size
                                            )  

    if gold_data:
        max_depth = max(gold_max_depth, max_depth) 
        max_width = max(gold_max_width, max_width)

    fig.update_layout(
                    yaxis=dict(range=[0,max_depth+1], autorange="reversed" if reverse else None),
                    xaxis=dict(range=[0,max_width+1])
                    )
    

    axis = dict(
                showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
            )

    fig.update_layout(
                        title=title,
                        #annotations=make_annotations(name2pos),
                        font_size=12,
                        showlegend=True,
                        margin=dict(l=40, r=40, b=85, t=100),
                        hovermode='closest',
                        plot_bgcolor="white", #'rgb(248,248,248)',
                        xaxis=axis,
                        yaxis=axis
                        )
    
    if save_to:
        fig.write_image(save_to)

    return fig