Explanation

Clone repository
----------------

Install bftools
----------------

bash install-bftools.sh
export PATH=$PATH:~/packages/bftools

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

mkdir scratch
python scripts/quick_convert_to_ids.py local-data/example_image_dir scratch myids