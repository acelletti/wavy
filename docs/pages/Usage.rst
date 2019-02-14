*************
Usage
*************

Read File
-------------

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
-------------

To read the file information without loading the data use ``wavy.info``:

.. code-block:: python

   >>> wavy.info("audio.wav")
   WaveFileInfo(sample_width=16, framerate=44100, n_channels=2, n_frames=286653, tags=None)