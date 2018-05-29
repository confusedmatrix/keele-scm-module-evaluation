FROM jupyter/datascience-notebook

RUN pip install vega wordcloud

RUN jupyter labextension install @jupyterlab/vega3-extension