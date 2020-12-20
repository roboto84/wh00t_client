=================
wh00t_client
=================

Simple python LAN chat client app with emoji support

.. image:: images/wh00t_client.png
    :scale: 50

Installation
------------
This project is managed with Python Poetry (https://github.com/python-poetry/poetry). With Poetry installed correctly,
simply clone this project and run::

    poetry install

To test the project, run::

    poetry run pytest

In order to run the program functions, see below.

Introduction
------------
This project functions as part of the larger wh00t project. This particular repository's purpose is
to act as a chat client.

wh00t_client.py
~~~~~~~~~~~~~~~~~~~~~~
This process functions as the wh00t chat client. wh00t_client.py requires that an ``.env`` file is available
in the *same* directory it is running under. The format of the .env file should contain ``SERVER_ADDRESS``, and
``SERVER_PORT`` as defined environmental variables.

| ``SERVER_ADDRESS`` : The chat server address
| ``SERVER_PORT`` : The port the chat server is listening on

An explained ``.env`` file format is shown below::

    SERVER_ADDRESS=<Server address>
    SERVER_PORT=<Server port>

A typical ``.env`` file may look like this::

    SERVER_ADDRESS=192.168.0.102
    SERVER_PORT=3001

To run the script once the environment (.env) file is created, from within the wh00t_server directory, simply type::

    poetry run python wh00t_client/wh00t_client.py

Commit Conventions
----------------------
Git commit conventions follows Conventional Commits message conventions explained in detail on their website
(https://www.conventionalcommits.org)


