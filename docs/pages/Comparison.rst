*************
Comparison
*************

The following table shows a comparison of supported functionality:

.. csv-table::
   :header: "Functionality", "builtin.wave", "scipy.wave", "wavy"
   :class: comparison
   :widths: 70, 20, 20, 20

   **RIFF Format Support**,         |check-circle|, |check-circle|, |check-circle|
   **RIFX Format Support**,         |times-circle|, |check-circle|, |check-circle|
   **Read Audio Information**,      |check-circle|, |times-circle|, |check-circle|
   **Read Data As Array**,          |times-circle|, |check-circle|, |check-circle|
   **Read Tag Information**,        |times-circle|, |times-circle|, |check-circle|

The following table shows a comparison of supported formats for uncompressed WAVE files:

.. table::
   :class: comparison
   :widths: 30, 40, 20, 20, 20

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
