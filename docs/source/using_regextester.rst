======================
Using the Regex tester
======================

The regex tester is a simple to use tester for checking the output of a program. It gives a point for every regex
matched.

File Format
+++++++++++

It has a simple file format. Every line follows the format of ``Field: Value`` and for most fields the first one
encountered is the one that's used.

The fields are:

    - *NAME: The name of the test
    -  MAIN: An alternative main class to use
    -  STDIN: The path to a file to feed to the program's stdin (can be relative to the configuration directory)
    - *Regex: A regular expression to test for. This one can be listed multiple times, and each one is tested for a match

The first line of the file needs to be ``#RegexTester`` to be detected

How it scores
+++++++++++++

It simply checks each regex given in the configuration file against the programs output. If there is a match anywhere
in the output it adds a point to the score. The maximum possible score is the total number of regexes in the configuration.