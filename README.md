# Keele university SCM module evaluation application
This application builds assets for a simple module evaluation (e.g. attainment histograms, student feedback histograms etc) and presents them as a HTML webpage.


## Dependencies
This application runs in a docker environment, therefore you only need a recent version of docker to run it.

Download and install docker if you haven't already: https://store.docker.com/search?type=edition&offering=community

Make sure you are signed into docker hub using a Docker ID (you may need to set this up if you haven't already got one) via the docker control panel. 

You will also need `make` in order to run the simple make commands provided.

## Installation and run with one command!
To install the docker environment, all the required dependecies and to serve the application, simply run:

```
make run
```

Once complete, the application will be served at `localhost`.

## Generating the module evaluation assets
The application is pre-loaded with a small amount of past data. To load your own files, you must drop the files into `data/raw/modules` in order for the script to generate assets for them. The format for the file structure should be:

```
python
    data
        raw
            modules
                MAT-10044
                    feedback.csv
                    grades.csv
            staff-feedback.csv
```

Once the files are in place, simply load the application (see above) and click the "Regenerate all data" button.

## Generating the web page with bundled assets
To build a the frontend assets from source, run:

```
make web.build
```

Once complete, the html, javscript, css and assets copied to the ` python/src/static` directory for serving by the application.

## Miscellaneous

### Running Jupyter notebook

To fiddle around with the stats/assets that are produced for the module evaluation you may run the provided jupyter notebook using the command:

```
make jupyter
```

Follow the link provided on the command line to open jupyter lab in your browser.

Any changes you make here that you want to keep will need to modified in `python/src` also

### Running the environment for webpage/bundle development

To change the code for displaying the webpage and building the resulting bundle, run the command:

```
make web.develop
```

The development server will run at `localhost:1234`
