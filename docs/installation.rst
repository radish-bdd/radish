Installation
============

radish is available as a Python 3 package on PyPI and thus installable with *pip*.

System Wide Installation
------------------------

To install radish system wide use the following *pip* command:

.. code:: bash

   pip install radish-bdd

**Note**: Make sure your user has enough privileges to install a package to the systems folders.

virtualenv Installation
-----------------------

To install radish in a *virtual python environment* use the following commands:

.. code:: bash

   virtualenv radish-env -p python3
   source radish-env/bin/activate
   pip install radish-bdd

Install from source
-------------------

To install radish from source you can clone the GitHub repository and use setuptools:

.. code:: bash

   git clone https://github.com/radish-bdd/radish
   cd radish
   python setup.py install
