


## Installation

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

6. make migrations
    ```
        ./manage.py makemigrations server
        ./manage.py makemigrations auth
        ./manage.py makemigrations admin
    ```

7. run migrations
    ```
        ./manage.py migrate
    ```

8. create an admin user
    ```
        ./manage.py createsuperuser     # follow the prompt
    ```

9. run server
    ```
        ./manage.py runserver
    ```
