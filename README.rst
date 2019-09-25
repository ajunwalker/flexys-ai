.. -*- mode: rst -*-

|Travis|_ |Codecov|_

.. |Travis| image:: https://travis-ci.com/ajunwalker/flexys-ai.svg?branch=master
.. _Travis: https://travis-ci.com/ajunwalker/flexys-ai

.. |Codecov| image:: https://codecov.io/gh/ajunwalker/flexys-ai/branch/master/graph/badge.svg
.. _Codecov: https://codecov.io/gh/ajunwalker/flexys-ai

Flexys AI
=====

Flexys is a django web application that automatically performs automated data analysis and machine learning.

Installation
------------

Flexys has been tested to work with the following packages:

- Django==2.2.5
- djangorestframework==3.10.3
- GPyOpt==1.2.5
- matplotlib==3.1.1
- pandas==0.24.1
- scikit-learn==0.21.2

How to run
---------------

Type the code below to start the web application::

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
