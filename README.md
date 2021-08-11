# UpSetPlotly

Generate UpSetPlot-style plots in the Plotly framework.

```shell
pip install UpSetPlotly
```

```python
from upsetplotly import UpSetPlotly

samples = [[1, 2, 3, 4], [2, 3, 4], [2, 5, 6]]
names = ["sample 1", "sample 2", "sample 3"]

usp = UpSetPlotly(samples, names)
usp.plot()
```

![](.README_images/basic_upsetplot.png)

The intersections can be ordered by passing `order_by={'increasing', 'decreasing'}`

```python
usp.plot(order_by='decreasing')
```
![](.README_images/decreasing_upsetplot.png)

Larger sets are okay too.

```python
import random

names = [f'sample_{i}' for i in range(1, 6)]
samples = [[''.join(random.choices('abcdefghijk', k=3)) for x in range(random.randint(1000, 3000))] for i in range(5)]

usp = UpSetPlotly(samples, names)
usp.plot()
```

![](.README_images/bigger_example.png)

But there would soon be too many possible intersections to realistically visualize them all. 
We can pass `intersection_limit='by_total 0.05'` to filter out any intersections which are smaller
that 5% of the total number of unique elements. Any float between 0 and 1 is acceptable.

```python
usp.plot(order_by='increasing', intersection_limit='by_total 0.05')
```

![](.README_images/bigger_example_by_total_filter.png)

Similarly, we can pass `intersection_limit='by_sample 0.05` to filter out any intersections which
do not comprise at least 5% of any sample.

```python
usp.plot(order_by='increasing', intersection_limit='by_sample 0.05')
```

![](.README_images/bigger_example_by_sample_filtered.png)

Additional data describing the elements can be passed to generate secondary plots above the 
UpSet plot.

```python
all_elements = set()
all_elements.update(*[set(x) for x in samples])
additional_data = {element: random.normalvariate(0, 1) for element in all_elements}
usp.add_secondary_plot(data=additional_data, label='Random stuff', plot_type='box')
```

![](.README_images/w_secondary_boxplot.png)

We can also do violin or swarm plots, or all three.

```python
usp = UpSetPlotly(samples, names)
usp.add_secondary_plot(data=additional_data, label='Random stuff', plot_type='box')
usp.add_secondary_plot(data=additional_data, label='Random stuff', plot_type='violin')
usp.add_secondary_plot(data=additional_data, label='Random stuff', plot_type='swarm')
usp.plot()
```

![](.README_images/w_all_secondary_plots.png)

See [dev_notes.md](./dev_notes.md) for plans and development progress.