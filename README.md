# HotViz

HotViz is a small visualization library.

## HotTree

A tree-plot is a plotly figure for visualizing tree structures. Example below visualizes the structure within an argument from a student essay. 

```python
from hotviz import hot_tree
from hotviz.example import tree_data

hot_tree(tree_data, title="Argument X")
```

HotTree also supports visulization of Gold vs Predicted data; Gold data will be opaque in the background and Prediction data in the forground.

```python
hot_tree(your_pred_data, gold_data=your_gold_data)
```

![](https://github.com/AxlAlm/hotviz/blob/setup/hotviz/example/tree_example.gif)
