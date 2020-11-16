
import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
from pprint import pprint
import time
from collections import Counter



def create_trees(items):
    """
    Parse a list of ints where each int value is interpreted as the point where to where the current index is linked.
    Creates a tree structured dict.
    """
    
    def place_node(tree_nodes, node, linked_node, plot_data):
        """
        This recursive function, given a node and the linked node (the node which the node links to),
        will go through the tree node by node and see if the subnodes of a node is == linked node.

        Its a greedy search.

        """

        # For each node we look for its link in other nodes, if link exists we add node as subtree to the
        # linked node.
        # We set column and row as following:
        # column = nr of subtrees of the parent
        # row = row of parent + 1
        #
        # NOTE! we will later update the columns given the width of each tree.
        # So, we create a mask for selecting the parts we might need to confiugre later
        # a) tree
        # b) tree rows 
        # c) root nodes
        #
        # when we have the order of the column and rows and max width
        # we can apply the following calculations to fix all coordinates
        # 
        # a = max(number rows on all levels)
        # c = biggest_row
        # for each row:
        #   if row > biggest row:
        #       new_columns_coordiantes
        #   else:
        #       space = a / nr nodes on row
        #       new_columns_coordiantes = [i*space for i in row_positions]
        #

        if linked_node in tree_nodes:
            parent_node = tree_nodes[linked_node]
            root = parent_node["root"]

            row = parent_node["row"] + 1

            if row not in plot_data["level_widths"]:
                plot_data["level_widths"][row] = 0
            
            plot_data["level_widths"][row] += 1
            column = plot_data["level_widths"][row]

            plot_data["X"].append(column)
            plot_data["Y"].append(row)
            plot_data["root"].append(root)
            plot_data["Xlink"].extend([parent_node["column"], column, None])
            plot_data["Ylink"].extend([parent_node["row"], row, None])
            plot_data["labels"].append(node)
            plot_data["max_depth"] = max(plot_data["max_depth"], row)
            plot_data["max_widths"][root] = max(plot_data["max_widths"][root], column)

            parent_node["subnodes"][node] =  {
                                                "row":row,        
                                                "column":column,
                                                "root":root, 
                                                "subnodes":{}
                                                }
            return True
        else:
            for node_id, node_dict in tree_nodes.items():
                if place_node(node_dict["subnodes"], node, linked_node, plot_data):
                    return True
                    
            return False

    plot_data = {
                "X":[],
                "Y":[], 
                "Xlink":[], 
                "Ylink":[],
                "labels": [],
                "root":[], 
                "max_depth":0, 
                "max_widths":{},
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
            trees[node] = {
                            "row":row,        
                            "column":column,
                            "root":node, 
                            "subnodes":{}
                            }
            plot_data["X"].append(column)
            plot_data["Y"].append(row)
            plot_data["root"].append(node)
            plot_data["labels"].append(node)
            plot_data["max_widths"][node] = 1
            plot_data["level_widths"] = {row:1}
            found = True
        else:
            found = place_node(trees, node, linked_node, plot_data)
    

        # if node found a place we remove it else we just add it
        # last to the unplaced_nodes list
        #node_tuple = unplaced_nodes.pop(0)
        if not found and (node, linked_node) not in unplaced_nodes:
            unplaced_nodes.append((node, linked_node) )

    pprint(trees)
    pprint(plot_data)
    for k,v in plot_data.items():
        if type(v) == int:
            continue
        print(k,len(v))
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


def create_tree_plot(fig, nodes:list, links:list, color:str):

    nodes_ids = create_ids(nodes)

    print(Counter(links))
    link_nodes_ids = [nodes_ids[i] for i in links]
    node_links = list(zip(nodes_ids,link_nodes_ids))

    plot_data = create_trees(node_links)
    
    # #TODO where do we start
    # # fix the distances
    # print("HELLO", width, depth)
    # max_width = width + 2
    # max_depth = depth + 2
    # X, Y, Xlink, Ylink, labels = parse_tree(
    #                                         my_tree, 
    #                                         max_depth=max_depth,
    #                                         max_width=max_width
    #                                         # start_column=3,
    #                                         # end_column=max_width,
    #                                         # row=depth,
    #                           
    # 
    # 
    # 
    # 
    #               )


    X = plot_data["X"]
    Y = plot_data["Y"]
    Xlink = plot_data["Xlink"]
    Ylink = plot_data["Ylink"]
    labels = plot_data["labels"]

    max_depth = 5
    max_width = 5

    name2pos = {}
    for i,l in enumerate(labels):
        name2pos[l] = (X[i],Y[i])
    
    
    fig.add_trace(go.Scatter(
                            x=X,
                            y=Y,
                            mode='markers',
                            name='bla',
                            marker=dict(symbol='circle-dot',
                                            size=25,
                                            color='#6175c1',    #'#DB4551',
                                            line=dict(color='rgb(50,50,50)', width=1)
                                            ),
                            text=labels,
                            hoverinfo='text',
                            opacity=0.8
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
                            hoverinfo='none'
                            ))

    fig.update_layout(
                        annotations=make_annotations(name2pos),
                        )
    
    return name2pos


def hot_tree(gold, pred=None):


    fig = go.Figure()

    #creating gold tree
    name2pos = create_tree_plot(fig, 
                                nodes=gold["nodes"], 
                                links=gold["links"], 
                                color="red"
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