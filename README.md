
# HotViz

HotViz is a small visualization library.

## install
```
pip install hotviz
```

## HotTree

A tree-plot is a plotly figure for visualizing tree structures. Example below visualizes the structure within an argument from a student essay. 

```python
from hotviz import hot_tree

hot_tree(MY_DATA)
```
![](https://github.com/AxlAlm/hotviz/blob/main/hotviz/example/example_tree_plot.png)

HotTree also supports visulization of Gold vs Predicted data; Gold data will be opaque in the background and Prediction data in the forground.

Input data should be a list of dicts comprising of the following feilds:
```python

  {
  'label': LABEL OF A NODE, 
  'link': IDX TO LIKED NODE, 
  'link_label': LABEL OF TH LINK, 
  'text': HOVER TEXT
  }
```

## HotText

A text highlighter where colors reflect the scores given for each token. This can be useful when wanting to visualize the confidence scores for a given class or the attention in a nn.

HotText also supports visulization of gold and predited spans so that one can see where the prediction differs from the gold.


```python
from hotviz import hot_text

hmtl = hot_text(    
                MY_SPAN_DATA, 
                labels=["MajorClaim", "Claim", "Premise"], 
                save_path="/tmp/hot_text.png",
                print_html=False, 
                show_spans=True,
                show_scores=True
                )
```

![](https://github.com/AxlAlm/hotviz/blob/main/hotviz/example/example_span.png)

Input data should be a list of dicts comprising of the following feilds. Note "gold" is optional

```python
{
  "token": TOKEN, 
  "pred": {
          "span_id": ID OF THE PREDICTED SPAN, 
          "label": LABEL OF THE PREDICTED SPAN, 
          "score": CONFIDENCE SCORE (will set the strength of color)
          }, 
          
  "gold": {
          "span_id": ID OF GOLD SPAN, 
          "label": LABEL OF FOLD SPAN, 
          "score": CONFIDENCE SCORE (will set the strength of color)
          }
 },
```

TODO: 
- improve the clarify of how breaks are visualized in hot_text
