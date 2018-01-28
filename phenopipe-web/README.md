# Phenopipe Server + Web Interface

This folder contains the code for the main phenopipe server with the main database and the corresponding web interface. 

The server side is written in Python with use of the Flask framework. 

For Migrations of the database the Alembic tool for SQLAlchemy is used.

The client side is written in Typescript using Angular and the Angular-CLI


## Prerequisites

 * Unix based server environment (currently only tested on CentOS7)
 * Redis 
 * OpenLDAP
 * Postgres Database
 * Webserver e.g. nginx or apache
 
 ## Installation
 
 In the following the installation procedure is explained briefly.
 For a more in depth description consult the wiki.
 

 1. Fill the server config file with the correct values for your environment.
     * Printer IP
     * Analysis server IP
     * Posprocess server IP
     * ...
 1. Deploy the Flask application
 1. Deploy the Angular application
 1. Set up your webserver to serve the Angular client application and the API exposed by the Flask application
 1. Configure uwsgi to start the application via the provided app.ini file (adapt the configuration if necessary)
 
 
 ## Features
 
  * Create Experiments
    * Including multiple sample groups with additional metadata
  * Print labels for later identification
  * View Timestamps created by the phenobox
    * Delete single Snapshots from a timestamp
  * Upload IAP Pipelines to the analysis server
  * Upload custom R Scripts for postprocessing of analysis results
  * Analyse Timestamps with different IAP pipelines
  * Postprocess Analysis results with custom R Scripts
    * Option to exclude certain snapshots from a Postprocess
  * View Status of Analysis/Postprocessing
 
 

