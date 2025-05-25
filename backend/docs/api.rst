===
API
===

LynrieScoop provides a comprehensive REST API for managing all aspects of cinema operations.

Authentication
=============

Most endpoints require authentication using JWT tokens. To authenticate:

1. POST to ``/api/auth/login`` with valid credentials
2. Use the returned token in the Authorization header as: ``Bearer {token}``

API Endpoints
============

Movies
------

.. py:module:: app.api.routes.movies

.. autofunction:: get_movies
.. autofunction:: get_movie
.. autofunction:: create_movie
.. autofunction:: update_movie
.. autofunction:: delete_movie

Cinemas
-------

.. py:module:: app.api.routes.cinemas

.. autofunction:: get_cinemas
.. autofunction:: get_cinema
.. autofunction:: create_cinema
.. autofunction:: update_cinema
.. autofunction:: delete_cinema

Screenings/Showings
-----------------

.. py:module:: app.api.routes.showings

.. autofunction:: get_showings
.. autofunction:: get_showing
.. autofunction:: create_showing
.. autofunction:: update_showing
.. autofunction:: delete_showing

Bookings
-------

.. py:module:: app.api.routes.bookings

.. autofunction:: get_bookings
.. autofunction:: get_booking
.. autofunction:: create_booking
.. autofunction:: update_booking
.. autofunction:: delete_booking

Users
-----

.. py:module:: app.api.routes.users

.. autofunction:: get_users
.. autofunction:: get_user
.. autofunction:: create_user
.. autofunction:: update_user
.. autofunction:: delete_user

Authentication
------------

.. py:module:: app.api.routes.auth

.. autofunction:: login
.. autofunction:: register
.. autofunction:: refresh_token
