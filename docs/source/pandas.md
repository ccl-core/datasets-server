# Pandas

[Pandas](https://pandas.pydata.org/docs/index.html) is a popular DataFrame library for data analysis.

To read from a single Parquet file, use the [`read_parquet`](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html) function to read it into a DataFrame:

```py
import pandas as pd

df = (
    pd.read_parquet("https://huggingface.co/datasets/tasksource/blog_authorship_corpus/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet")
    .groupby('sign')['text']
    .apply(lambda x: x.str.len().mean())
    .sort_values(ascending=False)
    .head(5)
)
```

To read multiple Parquet files - for example, if the dataset is sharded - you'll need to use the [`concat`](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) function to concatenate the files into a single DataFrame:

```py
urls = ["https://huggingface.co/datasets/tasksource/blog_authorship_corpus/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet", "https://huggingface.co/datasets/tasksource/blog_authorship_corpus/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet"]

df = (
      pd.concat([pd.read_parquet(url) for url in urls])
      .groupby('sign')['text']
      .apply(lambda x: x.str.len().mean())
      .sort_values(ascending=False)
      .head(5)
)
```
