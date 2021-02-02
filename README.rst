Explanation

Clone repository
----------------

Clone or download the code repository.

Install bftools
----------------

Next install bioformats tools:

.. code-block:: bash

    bash install-bftools.sh
    export PATH=$PATH:~/packages/bftools
    bfconvert -version

The last command checks that the install has worked by printing the bioformats
version.

Create Python virtualenv
------------------------

Create the Python virtual environment:

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate

Install requirements:

.. code-block:: bash

    pip install -r requirements.txt


Test image conversion
---------------------

To test the image conversion, first create a folder called ``local-data``. Then
copy some test .czi files into that folder. Then, to test the conversion:

.. code-block:: bash

    mkdir scratch
    python scripts/quick_convert_to_ids.py local-data scratch myids
