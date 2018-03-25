*************
Introduction
*************

A pure python module for working with WAVE files with support for all common file formats for both RIFF and RIFX.

When working with WAVE files, there are two main pure python modules available:

* *builtin.wave*
   Python built-in module, lacks support for float and 24bit integer.
   Provides raw data instead of an array of values.

* *scipy.wave*
   Scipy does not support 24bit integer files. The module strength and weakness is its simplicity,
   if all you need to do is read and write, this might be for you.

The **wave** module provides a fully featured, dedicated module that can be used as an alternative to the above if
flexibility and ease of use are desirable.
