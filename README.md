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

```python
usp.plot(order_by='decreasing')
```
![](.README_images/decreasing_upsetplot.png)
See [dev_notes.md](./dev_notes.md) for plans and development progress.