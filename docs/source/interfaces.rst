===============
User Interfaces
===============

This document describes the user interface interactions. There are currently two user interfaces in use, a Qt-based one
and a text based one, each one will be described in more detail on separate pages.

The only interface that is bundled in the base package in the text-based one, as this is seen as the minimal requirement
for usability. Any other provided interface should be a separate package and it should be self-contained. No changes
to the base package should be made solely to support the new interface (potentially with the exception of
 refactoring existing code). The qt package is a good example of this.

 .. toctree::

    textinterface
    qtinterface
