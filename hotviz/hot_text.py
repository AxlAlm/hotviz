    
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib as mpl
import json
import imgkit
import base64
from lxml import etree, html
from IPython.display import Image


def get_color_hex(cmap_name:str, value=1.0):
    norm = mpl.colors.Normalize(vmin=0.0,vmax=2)
    cmap = cm.get_cmap(cmap_name)
    hex_code = colors.to_hex(cmap(norm(value)))
    return hex_code

# def get_label2color(labels:list, style_elems:list, norm:None):
#     #header = ["<span> Classes: </span>"] 
#     label2cmap = {}
#     #color_ranges = ["Reds", "Blues", "Greens", "Oranges", "Purples"]
#     color_ranges =  ['Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
#                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
#                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
#     for i,label in enumerate(labels):
#         cmap = cm.get_cmap("Greens")
#         #hex_code = colors.to_hex(cmap(norm(1.0)))
#         #style_elems.append(f'.c{label} {{ background-color: {hex_code}; }}')
#         #header.append(f'<span class="c{label}">  {label}  </span><span> |</span>')
#         label2cmap[label] = cmap

#     #header.append("<br><br>")
#     return label2cmap


def under_overline(hex_code_bot, hex_code_top, token):
    return f'<span style="border-bottom: 3px dashed {hex_code_bot}; padding-bottom: 2px; border-top: 3px solid {hex_code_top}; padding-top: 2px;">{token}</span>'


def overline(hex_code, token):
    return f'<span style="border-top: 3px solid {hex_code}; padding-top: 2px;">{token}</span>'


def underline(hex_code, token):
    return f'<span style="border-bottom: 3px solid {hex_code}; padding-bottom: 2px;">{token}</span>'


def get_span2cmap(spans:list, span2label:dict):

    color_ranges =  [
                     'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','Greys',
                     'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                     'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
                     ]

    nr_color_ranges = len(color_ranges)-1
    nr_spans = len(spans)-1

    span2cmap = {}
    cmap2span = {}

    ci = 0
    i = 0
    duplicate_colors = False
    _set = False
    while i <= nr_spans:

        if ci > nr_color_ranges:
            duplicate_colors = True
            ci = 0

        span_id = spans[i]
        color = color_ranges[ci]

        #if we have more spans than ids we need to iterrate over colors again 
        # but make sure we dont pick the same color for spans with different labels
        if duplicate_colors:
            #print(cmap2span)
            current_color_holder = cmap2span[color]

            current_label = span2label[current_color_holder]
            label = span2label[span_id]

            #print(current_label, label, current_label != label)
            if current_label != label:
                ci += 1
                continue
        



        span2cmap[span_id] = color
        cmap2span[color] = span_id

        i += 1
        ci += 1

    return span2cmap


def get_legend(gold_label2span:dict, pred_label2span:dict, gold_span2cmap:dict, pred_span2cmap:dict, show_spans:bool, show_scores:bool):

    def get_color_blocks(label2span:dict, span2cmap:dict):

        color_blocks = []
        for label, span_ids in label2span.items():

            label_block = []
            for i in span_ids:
                hex_code = get_color_hex(span2cmap[i], 1.0)
                label_block.append(f'<span style="background-color:{hex_code}; color:{hex_code};">ok</span>')
                #label_block.append(f'<span style="background-color:{hex_code}; color:white;">{span2cmap[i]}    </span>')

            color_block = f'<span>| {label}</span>: {"".join(label_block)}'
            color_blocks.append(color_block)

        return color_blocks


    legend = f"""
            <span>Gold <span style="border-top: 4px solid black;"> solid </span>{''.join(get_color_blocks(gold_label2span, gold_span2cmap))}</span><br>
            <span>Pred <span style="border-bottom: 4px dashed black;"> dashed </span>{''.join(get_color_blocks(pred_label2span, pred_span2cmap))}</span><br>
            """
    if show_scores:
        certainty_span = [f'<span style="background-color:{get_color_hex("Greys",i)}; color:{get_color_hex("Greys",i)};">ok</span>' for i in np.linspace(0.0, 1.0, num = 10)]
        legend += ''.join(certainty_span)

    return legend


def get_mappings(data:list, key:str):

    spans = set()
    label2span = {}
    span2label = {}

    for d in data:
        span_id = d.get(key,{}).get("span_id", None) 
        label = d.get(key,{}).get("label", None)

        if span_id:
            spans.add(span_id)

        if label and span_id:

            if label not in label2span and label:
                label2span[label] = set()

            if span_id not in span2label:
                span2label[span_id] = label

            label2span[label].add(span_id)
            
    spans = sorted(spans)
    return spans, label2span, span2label
    

def hot_text(data, labels:list, save_path:str="/tmp/hot_text.png", print_html:bool=False, show_spans:bool=True, show_scores:bool=True, font:str="Verdana"):
    
    style_elems = [ 
                    "span { line-height: 30px; font-size:small;}",
                   ]


    puncts = set([".", "?", "!"])
    puncts_plus = set([","]) | puncts

    gold_spans, gold_label2span, gold_span2label = get_mappings(data, key="gold")
    pred_spans, pred_label2span, pred_span2label = get_mappings(data, key="pred")

    gold_span2cmap = get_span2cmap(gold_spans, gold_span2label)
    pred_span2cmap = get_span2cmap(pred_spans, pred_span2label)

    legend = get_legend(
                        gold_label2span=gold_label2span,
                        pred_label2span=pred_label2span, 
                        gold_span2cmap=gold_span2cmap, 
                        pred_span2cmap=pred_span2cmap,
                        show_spans=show_spans, 
                        show_scores=show_scores
                        )

    gold_spans = []
    pred_spans = []
    token_stack = []

    last_pred_span = ""
    last_gold_span = ""
    make_upper = True
    for i,td in enumerate(data):

        pred = td["pred"]
        score = pred.get("score", 1.0)
        pred_label = pred.get("label", None)
        pred_span_id = pred.get("span_id")

        if pred_label not in labels:
            pred_label = None

        gold = td.get("gold", {"label":None, "span_id":None})
        gold_label = gold.get("label", None)
        gold_span_id = gold.get("span_id")

        token = td["token"]
        
        ## Fixing Capitalization
        if make_upper:
            token = token.capitalize()
            make_upper = False
        
        if token in puncts:
            make_upper = True
        
        try:
            next_token = data[i+1]["token"]
        except IndexError as e:
            next_token = " "

        ## Fixing spaces
        if next_token not in puncts_plus:
            token = f"{token} "

        if show_scores:
            if pred_label is not None:
                #if pred["label"] in label2cmap:
                color_hex = get_color_hex(pred_span2cmap[pred_span_id], score)
                style_elems.append(f'.c{i} {{ background-color: {color_hex}; }}')

                token = f'<span class="c{i}">{token}</span>'

        if show_spans:
            pred_span = pred["span_id"]
            gold_span = gold["span_id"]

            if pred_span and gold_span:
                hex_code_pred = get_color_hex(pred_span2cmap[pred_span_id], 1.0)
                hex_code_gold = get_color_hex(gold_span2cmap[gold_span_id], 1.0)
                token = under_overline(hex_code_pred, hex_code_gold, token)
            elif pred_span:
                hex_code = get_color_hex(pred_span2cmap[pred_span_id], 1.0)
                token = underline(hex_code, token)
            elif gold_span:
                hex_code = get_color_hex(gold_span2cmap[gold_span_id], 1.0)
                token = overline(hex_code, token)

            last_pred_span = pred["span_id"]    
            last_gold_span = gold["span_id"]
        
        if ">" not in token:
            token = f'<span>{token}</span>'

        token_stack.append(token)


    #span {{ font-family:"verdana", monospace; font-size: 20px; }} 
    html_string =  f""" <html>
                            <head>
                                <style>
                                {' '.join(style_elems)}
                                </style>
                            </head>
                            <body style="font-family:{font}; font-size:20px;">
                            {''.join(token_stack)}
                            <br>
                            <hr>
                            {legend}
                            </body>
                            </html>
                    """

    imgkit.from_string(html_string, save_path, options={'quiet':'', "width": 1400, "height":800})


    if print_html:
        document_root = html.fromstring(html_string)
        print(etree.tostring(document_root, encoding='unicode', pretty_print=True))