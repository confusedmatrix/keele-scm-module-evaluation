FROM jupyter/datascience-notebook

RUN pip install vega3 altair

RUN jupyter labextension install @jupyterlab/vega3-extension