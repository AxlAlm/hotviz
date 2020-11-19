    
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

    
def hot_text(data, labels:list, save_path:str="/tmp/hot_text.png", display:bool=True, return_html:bool=True):
    
    # this needs to be improved..
    style_elems = [ 
                    "span { line-height: 54px;}",

                    # ".start_pred {border: 2px solid red; padding: 5px; border-top:1px solid transparent; border-right:1px solid transparent;}",
                    # ".end_pred {border: 2px solid red; padding: 5px; border-top:1px solid transparent; border-left:1px solid transparent;}",
                    # ".mid_pred {border: 2px solid red; padding: 5px; border-top:1px solid transparent; border-left:1px solid transparent; border-right:1px solid transparent;}",
                    # ".start_gold {border: 2px solid gold; padding: 5px; border-top:1px solid transparent; border-right:1px solid transparent;}",
                    # ".end_gold {border: 2px solid gold; padding: 5px; border-top:1px solid transparent; border-left:1px solid transparent;}",
                    # "mid_gold {border: 2px solid gold; padding: 5px; border-top:1px solid transparent; border-left:1px solid transparent; border-right:1px solid transparent;}",

                    "gold {color: gold;}",
                    "red {color: red;}",
                    #".verticalLineGold { border-left: thick solid gold;}"
                    #".verticalLinePred { border-left: thick solid gold;}"
                    #".gold {text-decoration:overline; text-decoration-color:gold;, padding-top: 10px;}",
                    ".gold {border-top: 3px solid gold; padding-top: 10px;}",
                    ".pred {border-bottom: 3px solid red; padding-bottom: 10px;}",
                    ".gold_pred {border-bottom: 3px solid red; padding-bottom: 10px; border-top: 3px solid gold; padding-top: 10px;}",
                    ".supsub {position: absolute}",
                    ".subscript {display:block; position:relative; left:2px; top: 30px}",
                    ".superscript {display:block; position:relative; left:2px; top:-30px}",
                    ]

    # setting the color for each class and creating a header where you can see the color for each class
    #use_scores = "False"
    #if "score" in data[0]["pred"]:
    header, label2cmap = class_header(labels, style_elems)

    gold_spans = []
    pred_spans = []
    token_stack = []

    last_pred_span = ""
    last_gold_span = ""
    for i,td in enumerate(data):

        pred = td["pred"]
        gold = td.get("gold", {"label":None, "span_id":None})
        token = td["token"]
        if "score" in pred and "label" in pred:
            if pred["score"] != None and pred["label"] != None:
                cmap = label2cmap[pred["label"]]
                hex_code = colors.to_hex(cmap(pred["score"]))
                style_elems.append(f'.c{i} {{ background-color: {hex_code}; }}')
                token = f'<span class="c{i}">{token} </span>'


        if pred["label"] and gold["label"]:
            token = f'<span class="gold_pred">{token}</span>'
        elif pred["label"]:
            token = f'<span class="pred">{token}</span>'

        elif gold["label"]:
            token = f'<span class="gold">{token}</span>'

        # we got a new span
        # if gold["span_id"] != last_gold_span and not last_gold_span:
        #     token_stack.append("|")

        # if we have a new span that is not the first for pred
        if last_gold_span != gold["span_id"] and last_gold_span:
            pass
            #<gold>|</gold>
            #<span class='supsub'><sup class='superscript'>Sup</sup></span>
            #sup = f"<span class='supsub'><sup class='superscript'>{last_gold_span}</sup></span>"
            #token_stack.append(sup)

        # if we have a new span that is not the first for gold
        if last_pred_span != pred["span_id"] and last_pred_span:
            pass
            #<gold>|</gold>
            #sub = f"<span class='supsub'><sub class='subscript'>{last_pred_span}</sub></span>"
            #token_stack.append(sub)
        
        token_stack.append(token)
        last_pred_span = pred["span_id"]    
        last_gold_span = gold["span_id"]

    #span {{ font-family:"verdana", monospace; font-size: 20px; }} 
    html_string =  f""" <html>
                            <head>
                                <style>
                                {' '.join(style_elems)}
                                </style>
                            </head>
                            <body style="font-family:Verdana; font-size:20px;">
                            <br><br>
                            <br><br>
                            {' '.join(header)}
                            {' '.join(token_stack)}

                            <br><br>

                            </body>
                            </html>
                    """

    imgkit.from_string(html_string, save_path, options={'quiet':'', "width": 800, "height":600})
    Image(save_path)


    document_root = html.fromstring(html_string)
    print(etree.tostring(document_root, encoding='unicode', pretty_print=True))

    # if return_html:
    #     soup = bs(html_string, features="lxml")
    #     pretty_html = soup.prettify()
    #     return pretty_html
