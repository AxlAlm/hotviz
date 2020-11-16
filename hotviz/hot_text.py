    
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
import json
import imgkit
import base64

    
def hot_text(tokens, class_scores, preds, true, th_path):
    
    print(tokens)
    color_ranges = ["Reds", "Blues", "Greens", "Oranges", "Purples"]

    style_elems = []
    task2colors = {}
    task_marks = []

    # setting the color for each class and creating a header where you can see the color for each class
    if class_scores:
        task_marks.append("<span> Classes: </span>")
        for i,(task, scores) in enumerate(class_scores.items()):
            cmap = cm.get_cmap(color_ranges[i])
            off = (sum(scores) / len(scores)) * 0.0001
            normer = colors.Normalize(vmin=0-off, vmax=1.2+off)
            task_colors = [colors.to_hex(cmap(normer(x))) for x in scores]
            task2colors[task] = task_colors

            style_elems.append(f'.c{task} {{ background-color: {colors.to_hex(cmap(0.8))}; }}')
            task_marks.append(f'<span class="c{task}">{task}</span> <span> |</span>')

        task_marks.append("<br><br>")
        

    label2ID = {}
    label2currentlabel = {}
    pred_spans = []
    token_stack = []
    current_span_label = None
    for i in range(len(tokens)):
        
        if class_scores:
            top_class = ""
            highest_prob = -1
            for task, scores in class_scores.items():

                if scores[i] > highest_prob:
                    top_class = task
                    highest_prob = scores[i]
        
            style_elems.append(f'.c{i} {{ background-color: {task2colors[top_class][i]}; }}')
            token_stack.append(f'<span class="c{i}">{tokens[i]}</span>')
        
        else:
            token_stack.append(tokens[i])
            
            
        current_pred = preds[i]
        SEG, *label = current_pred.split("_")
        

        try:
            NEXT_SEG, *_  = preds[i+1]
        except IndexError as e:
            NEXT_SEG = "O"
        
        if not label:
            label = "seg"
        else:
            label = label[0]

        if label not in label2ID:
            label2ID[label] = 0
        
        if SEG == "B":
            pred_spans.extend(token_stack[:-1])
            token_stack = [token_stack[-1]]

            label2ID[label] += 1

        current_span_label = f"{label}_{label2ID[label]}"

        next_outside_or_new = NEXT_SEG in ["O", "B"]
        current_inside_or_begin = SEG in ["I","B"]
        if current_inside_or_begin and next_outside_or_new:
            
            pred_spans.append(f"|<u>{' '.join(token_stack)}</u>|<sup>{current_span_label}</sup>")

            token_stack = []


    pred_spans.extend(token_stack)        

    html_string =  f""" <html>
                            <head>
                                <style>
                                span {{ font-family:"verdana", monospace; font-size: 20px; }} 
                                {' '.join(style_elems)}
                                </style>
                            </head>
                            <body>
                            <br><br>
                            <br><br>
                            {' '.join(task_marks)}
                            {' '.join(pred_spans)}
                            </body>
                            </html>
                    """

    imgkit.from_string(html_string, th_path, options={'quiet':'', "width": 800, "height":600})

    with open(th_path, "rb") as f:
        enc_img = base64.b64encode(f.read())
        src = f"data:image/png;base64,{enc_img.decode()}"

    return src