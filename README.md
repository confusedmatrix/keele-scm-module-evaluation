# Keele university SCM module evaluation application
This application builds assets for a simple module evaluation (e.g. attainment histograms, student feedback histograms etc) and presents them as a HTML webpage.


## Dependencies
This application runs in a docker environment, therefore you only need a recent version of docker to run it.

Download and install docker if you haven't already: https://store.docker.com/search?type=edition&offering=community

Make sure you are signed into docker hub using a Docker ID (you may need to set this up if you haven't already go one) via the docker control panel. 

You will also need `make` in order to run the simple make commands provided.

## Installation
To intall the docker environment and all the required dependecies of the project, simply run:

```
make install
```

## Generating the module evaluation assets
For this to do anything useful, you must drop some files into `data/raw/modules` in order for the script to generate assets for them. The format for the file structure should be:

```
data
    raw
        modules
            MAT-10044
                feedback.csv
                grades.csv
        staff-feedback.csv
```

This command will generate all the assets required to be displayed on the webpage:

```
make analysis.run
```

Once complete, the JSON and images will be located in `data/generated`

## Generating the web page with bundled assets
To build a distributable production directory containing the web page and assets, run:

```
make web.build
```

Once complete, the html, javscript, css and assets will be located in `web/dist`

## Serve the webpage
To serve the resulting web package, run:

```
make web.serve
```

Now go to `localhost` in your browser to see the resulting web page.

## Miscellaneous

### Running Jupyter notebook

To fiddle around with the stats/assets that are produced for the module evaluation you may run the provided jupyter notebook using the command:

```
make analysis.develop
```

Follow the link provided on the command line to open jupyter lab in your browser.

Any changes you make here that you want to keep will need to modified in `analysis/main.py` also

### Running the environment for webpage/bundle development

To change the code for displaying the webpage and building the resulting bundle, run the command:

```
make web.develop
```

The development server will run at `localhost:1234`