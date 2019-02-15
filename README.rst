Wavy
=====

.. image:: https://travis-ci.org/acelletti/wavy.svg?branch=master
   :target: https://travis-ci.org/acelletti/wavy

.. image:: https://coveralls.io/repos/github/acelletti/wavy/badge.svg?branch=travisci
   :target: https://coveralls.io/github/acelletti/wavy?branch=travisci

.. image:: https://img.shields.io/appveyor/tests/acelletti/wavy.svg
   :target: https://ci.appveyor.com/project/acelletti/wavy/build/tests

.. image:: https://img.shields.io/github/license/acelletti/wavy.svg
   :target: https://opensource.org/licenses/MIT

.. image:: https://readthedocs.org/projects/wavy/badge/?version=latest
   :target: https://wavy.readthedocs.io/en/latest/?badge=latest

Introduction
------------

A pure python module for working with WAVE files with support for all common file formats for both RIFF and RIFX.

When working with WAVE files, there are two main pure python modules available:

* *builtin.wave*
   Python built-in module, lacks support for float and 24bit integer.
   Provides raw data instead of an array of values.

* *scipy.wave*
   Scipy does not support 24bit integer files. The module strength and weakness is its simplicity,
   if all you need to do is read and write, this might be for you.

The **wave** module provides a fully featured dedicated module that can be used as an alternative to the above if
flexibility and ease of use are desirable.


.. |check-circle| image:: https://upload.wikimedia.org/wikipedia/commons/5/50/Yes_Check_Circle.svg
                  :scale: 150%

.. |times-circle| image:: https://upload.wikimedia.org/wikipedia/commons/f/f5/No_Cross.svg
                  :scale: 150%

Comparison
^^^^^^^^^^^

The following table shows a comparison of supported functionality:

.. csv-table::
   :header: "Functionality", "builtin.wave", "scipy.wave", "wavy"

   **RIFF Format Support**,         |check-circle|, |check-circle|, |check-circle|
   **RIFX Format Support**,         |times-circle|, |check-circle|, |check-circle|
   **Read Audio Information**,      |check-circle|, |times-circle|, |check-circle|
   **Read Data As Array**,          |times-circle|, |check-circle|, |check-circle|
   **Read Tag Information**,        |times-circle|, |times-circle|, |check-circle|

The following table shows a comparison of supported formats for uncompressed WAVE files:

.. table::

   +--------------+------------+----------------+----------------+----------------+
   | Sample Width | Format Tag |  builtin.wave  |   scipy.wave   |      wavy      |
   +==============+============+================+================+================+
   |   **8 bit**  |     PCM    | |check-circle| | |check-circle| | |check-circle| |
   +              +------------+----------------+----------------+----------------+
   |              | EXTENSIBLE | |times-circle| | |check-circle| | |check-circle| |
   +--------------+------------+----------------+----------------+----------------+
   |  **16 bit**  |     PCM    | |check-circle| | |check-circle| | |check-circle| |
   +              +------------+----------------+----------------+----------------+
   |              | EXTENSIBLE | |times-circle| | |check-circle| | |check-circle| |
   +--------------+------------+----------------+----------------+----------------+
   |  **24 bit**  |     PCM    | |check-circle| | |times-circle| | |check-circle| |
   +              +------------+----------------+----------------+----------------+
   |              | EXTENSIBLE | |times-circle| | |times-circle| | |check-circle| |
   +--------------+------------+----------------+----------------+----------------+
   |  **32 bit**  |     PCM    | |check-circle| | |check-circle| | |check-circle| |
   +              +------------+----------------+----------------+----------------+
   |              | EXTENSIBLE | |times-circle| | |check-circle| | |check-circle| |
   +              +------------+----------------+----------------+----------------+
   |              |    FLOAT   | |times-circle| | |check-circle| | |check-circle| |
   +--------------+------------+----------------+----------------+----------------+
   |  **64 bit**  |    FLOAT   | |times-circle| | |check-circle| | |check-circle| |
   +--------------+------------+----------------+----------------+----------------+

Installation
-------------

The latest stable version is available on `PyPI <https://pypi.org/project/wavy/>`_.

Either add ``wavy`` to your ``requirements.txt`` file or install with pip:

.. code-block:: bash

   pip install wavy

Usage
-------

Read File
^^^^^^^^^^

Open a file using the module use ``wavy.read``:

.. code-block:: python

   >>> import wavy
   >>> file = wavy.read("audio.wav")
   >>> file
   WaveFile(sample_width=16, framerate=44100, n_channels=2, n_frames=286653)

Get the data for the file:

.. code-block:: python

   >>> rate, data = file.framerate, file.data

   >>> rate
   44100

   >>> data.shape
   (286653, 2)

   >>> data.dtype
   int16


Get File Info
^^^^^^^^^^^^^

To read the file information without loading the data use ``wavy.info``:

.. code-block:: python

   >>> wavy.info("audio.wav")
   WaveFileInfo(sample_width=16, framerate=44100, n_channels=2, n_frames=286653, tags=None)


Authors
-------

* **Andrea Celletti** - *Initial work* - `Profile <https://github.com/acelletti>`_, `Email <celletti.andrea87@gmail.com>`_

License
---------

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.
