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
from hotviz.example import tree_data

hot_tree(tree_data, title="Argument X")
```
![](https://github.com/AxlAlm/hotviz/blob/setup/hotviz/example/example_tree_hover.png)

HotTree also supports visulization of Gold vs Predicted data; Gold data will be opaque in the background and Prediction data in the forground.

```python
hot_tree(your_pred_data, gold_data=your_gold_data)
```

![](https://github.com/AxlAlm/hotviz/blob/setup/hotviz/example/tree_example.gif)



## HotText

A text highlighter where colors reflect the scores given for each token. This can be useful when wanting to visualize the confidence scores for a given class or the attention in a nn.

HotText also supports visulization of gold and predited spans so that one can see where the prediction differs from the gold.


```python
from hotviz import hot_text
from hotviz.example import span_data

hmtl = hot_text(    
                span_data, 
                labels=["X", "Z"], 
                save_path="/tmp/hot_text.png",
                print_html=False, 
                show_spans=True,
                show_scores=True
                )
```

![](https://github.com/AxlAlm/hotviz/blob/setup/hotviz/example/hot_text_example.png)

TODO: 
- add info legend to hot_text so one knows which span color is gold and predicted
- changing color of hot_text
- changing possition of span label text of hot_text
- adding breaks in spans for hot_text
