


## Installation

The Django DB module is plug-and-play i.e. it lets you choose the database backend.
PostgreSQL is the best choice, but it's a pain in the ass to set up and it's not
necessary during development. If you can't get it working, follow the "alternate
sqlite set up" instrctions. Once you've set up the DB, follow the "django set up"
instructions.



### PostgreSQL set up
1. install PostgreSQL
    ```bash
        sudo apt install postgresql
    ```
2. run psql as postgres
    ```bash
        su - postgres
        psql
    ```
    OR
    ```bash
        sudo su postgres
        psql
    ```

3. create cybotify user
    ```psql
        CREATE USER cybotify PASSWORD 'cybotify';
        ALTER ROLE cybotify SET client_encoding TO 'utf8';
        ALTER ROLE cybotify SET default_transaction_isolation TO 'read committed';
        ALTER ROLE cybotify SET timezone TO 'UTC';
    ```

4. create cybotify database and grant permissions
    ```psql
        CREATE DATABASE cybotify OWNER cybotify;
        GRANT ALL ON DATABASE cybotify TO cybotify;
        \q
    ```

5. open /etc/postgresql/12/main/pg_hba.conf and change "peer" to "md5" on this line:
    ```
        # "local" is for Unix domain socket connections only
        local   all             all                                     peer    <--- change to md5
    ```

### Alternate sqlite set up

1. switch to branch 'dev/sqlite'
    ```
        git checkout dev/sqlite
    ```
2. install SQLite
    ```
        sudo apt install sqlite
    ```


### Django set up

1. install python requirements
    ```
        pip install -r requirements.txt
        # for dev:
        pip install -r requirements_dev.txt (for git pre-commit hooks)
        pre-commit install
    ```

2. make migrations
    ```
        ./manage.py makemigrations accounts
        ./manage.py makemigrations auth
        ./manage.py makemigrations admin
        ./manage.py makemigrations music
        ./manage.py makemigrations stats
    ```

3. run migrations
    ```
        ./manage.py migrate
    ```

4. create an admin user
    ```
        ./manage.py createsuperuser     # follow the prompt
    ```

5. run server
    ```
        ./manage.py runserver
    ```
