# Web Semantic Project
Authors:

Hanane OUBOLOHOU  |   hanane.oublouhou@emse.fr

Yana SOARES DE PAULA  |   yana.soaresdepaula@emse.fr


# Instructions

1. Configure Apache Jena Fuseki :
    1. You must have Apache Jena Fuseki installed. If it's not installed, see this [link](https://jena.apache.org/documentation/fuseki2/#download-fuseki).
    1. Access the main folder of Fuseki via command line (in Linux, use `cd /path/to/apache/jena/fuseki`).
    1. In the command line, write `./fuseki-server --update --mem /ds` to create an **in-memory non-persistant** dataset in the server.
        * *Note:* `/ds` is the name of your dataset, if you change it, the codes provided in this project will not be well-configured.
        * *Note:* To create a **persistent** dataset, type `./fuseki-server --loc=/path/to/dataset /ds`.
    1. Leave the server as it is (do not close the terminal).
1. Install the required libraries `pip install -r requirements.txt` 
1. Run the `triplestore.py` file.
1. Run the `app.py` to launch the web server. You can access the web page on : http://127.0.0.1:5000/
