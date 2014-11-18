.. Substitutions

.. |Report| replace:: :py:class:`~moodlegradetool.reporting.Report`

.. |gen| replace:: :py:meth:`~moodlegradetool.reporting.Report.generate_report`

.. |save| replace:: :py:meth:`~moodlegradetool.reporting.Report.save`

.. |str| replace:: :py:meth:`~moodlegradetool.reporting.Report.__str__`

=====================
Understanding Reports
=====================

Subclasses of |Report| are for transforming the list of :py:class:`~moodlegradetool.student.Student` objects into
an externally usable representation, such as XML, PDF, CSV, ect. They are usually used after testing has been completed.

Making a new |Report| type is a fairly simple endeavor, just override a couple of methods and call register on your new
class.

Making reports
++++++++++++++

To make a new |Report| type you need to override |gen|, (optionally) |save|, and (optionally) |str|. |Report|'s __init__ method
will store the student list in an attribute called source.

.. note:: While overriding |save| and |str| is optional, if gen doesn't return a string object, overriding at least
          |str| is recommended.

|gen|
-----

|gen| is the method that actually makes the report. Use the students list to compile the report in whatever data type
you want.

|save|
------

|save| takes either a filename or a file-like object and writes the report to it. In it's default implementation, it
does ``str(self)`` and writes it to the file in question.

|str|
-----

Returns the object made by |gen| as a string. Defaults to ``str(self.generate_report()``.

