=====================
Getting Started Guide
=====================

Welcome to AutoDataSetBuilder! This guide will help you get up and running quickly.

Prerequisites
=============

- **Python 3.10+**: Ensure you have Python 3.10 or later installed
- **Docker & Docker Compose**: For running services locally (recommended)
- **Git**: For cloning the repository
- **~5 GB disk space**: For Docker images and data storage

Quick Installation (3 steps)
=============================

1. Clone the Repository
-----------------------

.. code-block:: bash

    git clone https://github.com/rajamuhammadawais1/AutoDataSetBuilder.git
    cd AutoDataSetBuilder

2. Start Services with Docker Compose
--------------------------------------

.. code-block:: bash

    docker-compose up -d

3. Verify Services
------------------

.. code-block:: bash

    docker-compose ps

You should see three services running:
- **minio** - Object storage (S3-compatible)
- **postgres** - Metadata database
- **label-studio** - Interactive labeling tool

Accessing Services
==================

After startup, access the services at:

- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

- **Label Studio**: http://localhost:8080
  - Create a new project to start labeling

- **PostgreSQL**: `postgresql://autods_user:autods_password@localhost:5432/autods_db`
  - Connect with any PostgreSQL client

Next Steps
==========

Now that services are running:

1. **Install the SDK**:

   .. code-block:: bash

       pip install -e .

2. **Run Your First Example**:

   .. code-block:: bash

       python examples/example_ingest_and_preprocess.py

3. **Check the Documentation**:

   - :doc:`/usage/sdk` - Python SDK usage
   - :doc:`/usage/services` - Docker services
   - :doc:`/usage/airflow` - Airflow orchestration

Troubleshooting
===============

**Ports Already in Use**

If ports 9000, 9001, 8080, or 5432 are already in use:

.. code-block:: bash

    # Stop existing containers
    docker-compose down
    
    # Or change ports in docker-compose.yml

**Database Connection Errors**

Ensure PostgreSQL is fully initialized:

.. code-block:: bash

    # Wait a few seconds and try again
    sleep 10
    
    # Check logs
    docker-compose logs postgres

**Out of Disk Space**

Docker images and data take ~5 GB:

.. code-block:: bash

    # Clean up old images
    docker system prune -a
    
    # Check disk usage
    du -sh *

Support
=======

- Check :doc:`/troubleshooting` for common issues
- Visit `GitHub Issues <https://github.com/rajamuhammadawais1/AutoDataSetBuilder/issues>`_
- Read :doc:`/faq` for frequently asked questions
