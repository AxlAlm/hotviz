    
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
import json
import imgkit
import base64
from lxml import etree, html
#from bs4 import BeautifulSoup as bs
from IPython.display import Image


def class_header(labels:list, style_elems:list):
    header = ["<span> Classes: </span>"] 
    label2cmap = {}
    color_ranges = ["Reds", "Blues", "Greens", "Oranges", "Purples"]
    for i,label in enumerate(labels):
        cmap = cm.get_cmap(color_ranges[i])
        hex_code = colors.to_hex(cmap(1.0))

        style_elems.append(f'.c{label} {{ background-color: {hex_code}; }}')
        header.append(f'<span class="c{label}">  {label}  </span><span> |</span>')
        label2cmap[label] = cmap

    header.append("<br><br>")
    return header, label2cmap

    
def hot_text(data, labels:list, save_path:str="/tmp/hot_text.png", return_html:bool=True, show_spans:bool=True, show_scores:bool=True, font:str="Verdana"):
    
    # this needs to be improved..
    style_elems = [ 
                    "span { line-height: 54px;}",
                    ".gold {border-top: 3px solid gold; padding-top: 5px;}",
                    ".pred {border-bottom: 3px solid red; padding-bottom: 5px;}",
                    ".gold_pred {border-bottom: 3px solid red; padding-bottom: 5px; border-top: 3px solid gold; padding-top: 5px;}",
                    ".supsub {position: absolute}",
                    ".subscript {display:block; position:relative; left:2px; top: 18px; font-size: 50%; font-weight:bolder;}",
                    ".superscript {display:block; position:relative; left:2px; top:-20px; font-size: 50%; font-weight:bolder;}",
                    ]

    header = []
    if show_scores:
        header, label2cmap = class_header(labels, style_elems)

    gold_spans = []
    pred_spans = []
    token_stack = []

    last_pred_span = ""
    last_gold_span = ""
    for i,td in enumerate(data):

        pred = td["pred"]
        gold = td.get("gold", {"label":None, "span_id":None})
        #token = f'<span>{td["token"]}</span>'
        token = td["token"]

        if show_scores:
            if "score" in pred and "label" in pred:
                if pred["score"] != None and pred["label"] != None:
                    cmap = label2cmap[pred["label"]]
                    hex_code = colors.to_hex(cmap(pred["score"]))
                    style_elems.append(f'.c{i} {{ background-color: {hex_code}; }}')
                    token = f'<span class="c{i}">{token} </span>'

        
        if show_spans:

            # if we dont have scores we just add some space so that the prediction
            # and gold lines drag over to begining of next word, hence leave the lines intact
            if not show_scores:
                token += " "

            pred_span = pred["span_id"]
            gold_span = gold["span_id"]

            if pred_span and gold_span:
                token = f'<span class="gold_pred">{token}</span>'
            elif pred_span:
                token = f'<span class="pred">{token}</span>'
            elif gold_span:
                token = f'<span class="gold">{token}</span>'

            # we got a new span
            # if gold["span_id"] != last_gold_span and not last_gold_span:
            #     token_stack.append("|")

            # if we have a new span that is not the first for pred
            if last_gold_span != gold["span_id"] and last_gold_span:
                #<gold>|</gold>
                #<span class='supsub'><sup class='superscript'>Sup</sup></span>
                sup = f"<span class='supsub'><sup class='superscript'>{last_gold_span}</sup></span>"
                token_stack.append(sup)

            # if we have a new span that is not the first for gold
            if last_pred_span != pred["span_id"] and last_pred_span:
                #<gold>|</gold>
                sub = f"<span class='supsub'><sub class='subscript'>{last_pred_span}</sub></span>"
                token_stack.append(sub)
            
            last_pred_span = pred["span_id"]    
            last_gold_span = gold["span_id"]
        
        token_stack.append(token)


    #span {{ font-family:"verdana", monospace; font-size: 20px; }} 
    html_string =  f""" <html>
                            <head>
                                <style>
                                {' '.join(style_elems)}
                                </style>
                            </head>
                            <body style="font-family:{font}; font-size:20px;">
                            <br><br>
                            <br><br>
                            {' '.join(header)}
                            {' '.join(token_stack)}

                            <br><br>

                            </body>
                            </html>
                    """

    imgkit.from_string(html_string, save_path, options={'quiet':'', "width": 800, "height":600})


    if return_html:
        document_root = html.fromstring(html_string)
        return etree.tostring(document_root, encoding='unicode', pretty_print=True)