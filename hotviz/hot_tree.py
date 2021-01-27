

#basics
from copy import deepcopy
import numpy as np

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
    # first part only alines the trees so they are equally distributed over the max width
    tree_level_mask = Y==1
    
    nr_trees = len(plot_data["tree_widths"])
    if nr_trees == 1:
        nr_trees += 1

    new_xs = X[tree_level_mask] * ( plot_data["max_width"] /   nr_trees)
    X[tree_level_mask] = new_xs
    plot_data["X"] = X.tolist()

    ## TODO:
    # we need to shift the subtrees of the main tree to make them look a bit nicer
    #
    # possible solutions:
    # shift each level for each tree according to :

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
            plot_data["labels"].append(node["id"])
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
            plot_data["root"].append(node["id"])
            plot_data["labels"].append(node["id"])
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
                    for i, l in enumerate(plot_data["labels"])]

    fig.update_layout(
                        annotations=annotations,
                        )


def create_ids(data):
    node_stack = {}
    for node in data:
        label = node["label"]

        if label not in node_stack:
            node_stack[label] = []
        
        node_id = f"{label}_{len(node_stack[label])}"
        
        node_stack[label].append(label)
        node["id"] = node_id


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
    

def add_lines(fig, plot_data, opacity:float, legendgroup:str):
    for label, link_data in plot_data["link_xy"].items():

        if not label:
            style = dict(color="black", width=2, dash='solid')
            showlegend = False 
        else:
            style = link_data["style"]
            showlegend = True

        fig.add_trace(go.Scatter(
                                x=link_data["X"],
                                y=link_data["Y"],
                                mode='lines',
                                name=label,
                                line=style,
                                hoverinfo="none",
                                showlegend=True if legendgroup is None else False,
                                legendgroup=legendgroup,
                                opacity=opacity,
                                ))


def add_nodes(fig, plot_data, colors:list, opacity:float, legendgroup:str):
    fig.add_trace(go.Scatter(
                            x=plot_data["X"],
                            y=plot_data["Y"],
                            mode='markers+text',
                            name=legendgroup,
                            marker=dict(symbol='diamond-wide',
                                            size=50,
                                            color=colors.pop(0),
                                            #opacity=colors,
                                            ),
                            text=plot_data["labels"],
                            hovertext=plot_data["texts"],
                            hoverinfo='text',
                            showlegend=False,
                            legendgroup=legendgroup,
                            opacity=opacity,
                            textposition='middle center'
                            
                            ))


def format_text(text:str):
    tokens = text.split(" ")
    return "<br>".join([" ".join(tokens[i:i+10]) for i in range(0,len(tokens),10)])


def reformat_links(data):
    label2idx = {d["label"]:i for i,d in enumerate(data)}

    for node in data:
        link  = node["link"]

        if isinstance(link, int):
            node["link_int"] = link
            node["link"] = data[link]["id"]
        else:
            node["link_int"] = label2idx[link]


def create_tree_plot(fig, data:dict, colors:str, reverse:bool, opacity:float=1.0, legendgroup:str=None): # nodes:list, links:list, color:str):

    data = deepcopy(data)
    colors = deepcopy(colors)

    #we turn labels into ids
    if "id" not in data[0]:
        create_ids(data)

    # change links to labels or add int to link_int so we can sort
    reformat_links(data)

    # sort data to untangle trees
    data = sorted(data, key=lambda x:x["link_int"])

    # parse the data to get plot data ( e.g. X Y coordinates, max depth, max width etc)
    plot_data = get_plot_data(data)

    #normalize coordinates to make tree abit nicer now as we know the depth and widths
    normalize_row_coordinates(plot_data)

    # when we have normalized X and Y corridnates we can set up all the links
    link_labels = sorted(set([d["link_label"] for d in data]))
    set_link_coordinates(plot_data, labels=link_labels, colors=colors)
    
    #create the plot
    add_lines(fig, plot_data, opacity=opacity, legendgroup=legendgroup)
    add_nodes(fig, plot_data, colors=colors, opacity=opacity, legendgroup=legendgroup)
    #add_node_text(fig, plot_data)
    
    return plot_data["max_depth"], plot_data["max_width"]


def hot_tree(data, gold_data=None, colors="Plotly", reverse=True, title:str="", save_to:str=None):

    fig = go.Figure()

    #get colors scale
    for scale in [px.colors.sequential, px.colors.qualitative, px.colors.cyclical]:
        if hasattr(scale, colors):
            colors = getattr(scale, colors) 
            break
            
    if not isinstance(colors,list):
        raise KeyError(f"{colors} is not a supported plotly colorscale. scales can be found here: https://plotly.com/python/builtin-colorscales/")
    
    # gold data is added , we can create a tree with high opacity that just sits static in the background
    if gold_data:
        replacement_legend(fig, "gold")
        gold_max_depth, gold_max_width = create_tree_plot(  
                                                            fig, 
                                                            data=gold_data,
                                                            colors=colors,
                                                            reverse=reverse,
                                                            opacity=0.3,
                                                            legendgroup="gold"
                                                            )

    legendgroup = None
    if gold_data:
        replacement_legend(fig, "pred")
        legendgroup = "pred"
    
    max_depth, max_width = create_tree_plot(  
                                            fig, 
                                            data=data,
                                            colors=colors,
                                            reverse=reverse,
                                            legendgroup=legendgroup
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