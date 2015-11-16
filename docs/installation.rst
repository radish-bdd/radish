Installation
============

radish is available as a python 2 and python 3 package on PyPI and thus installable with *pip* and *pip3*.

System Wide Installation
------------------------

To install radish system wide use the following *pip* command:

Python 2:

.. code:: bash

   pip install radish-bdd

Python 3:

.. code:: bash

   pip3 install radish-bdd

**Note**: Make sure your user has enough privileges to install a package to the systems folders.

virtualenv Installation
-----------------------

To install radish in a *virtual python environment* use the following commands:

Python 2:

.. code:: bash

   virtualenv radish-env -p python2
   source radish-env/bin/activate
   pip install radish-bdd

Python 3:

.. code:: bash

   virtualenv radish-env -p python3
   source radish-env/bin/activate
   pip install radish-bdd

Install from source
-------------------

To install radish from source you can clone the github repository and use setuptools:

Python 2:

.. code:: bash

   git clone https://github.com/radish-bdd/radish
   cd radish
   python2 setup.py install

Python 3:

.. code:: bash

   git clone https://github.com/radish-bdd/radish
   cd radish
   python3 setup.py install
