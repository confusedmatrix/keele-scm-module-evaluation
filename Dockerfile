FROM jupyter/datascience-notebook

RUN pip install vega3 altair openpyxl

RUN jupyter labextension install @jupyterlab/vega3-extension