## Keele university SCM module evaluation application
The application builds assets for a simple module evaluation (e.g. attainment histograms, student feedback histograms etc) and presents them as a HTML webpage.


## Dependencies
This application runs in docker environment, therefore you only need a recent version of docker to run it.

Download and install docker if you haven't already: https://store.docker.com/search?type=edition&offering=community

You will also need `make` in order to run the simple make commands provided.

## Installation
To intall thhe docker environment and all the required dependecies of the project, simply run:

```
make install
```

## Generating the module evaluation assets
For this to do anything useful, you must drop some files into `data/raw/modules` in order for the script to generate assets for them. The format for file structure should be:

```
data
    raw
        modules
            MAT-10044
                feedback.csv
                grades.csv
```

This command will generate all the assets required to be displayed on the webpage:

```
make analysis.run
```

## Generating the web page with bundled assets
To build a distributable production directory containing the web page and assets, run:

```
make web.build
```


## Serve the webpage
To serve the resulting web package, run:

```
make web.serve
```

## Miscellaneous

### Running Jupyter notebook

To fiddle around with the stats/assets that are produced for the module evaluation you may run the provided jupyter notebook using the command:

```
make analysis.develop
```

### Running environment for webpage/bundle development

To change the code for displaying the webpage and building the resulting bundle, run the command:

```
make web.develop
```