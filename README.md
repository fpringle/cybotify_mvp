# Cybotify MVP
<div>
  <a href="https://github.com/fpringle/cybotify_mvp/actions/workflows/push_tests.yml">
    <img src="https://github.com/fpringle/cybotify_mvp/actions/workflows/push_tests.yml/badge.svg" height="20" alt="Tests" title="Tests">
  </a>
  <a href="https://github.com/fpringle/cybotify_mvp/actions/workflows/push_tests.yml">
    <img src="images/coverage.svg" height="20" alt="Test coverage" title="Test coverage">
  </a>
</div>


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

1. change django backend for postgresql to sqlite
    ```
    # root-dir/cybotify/settings.py
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

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

5. put your app's client credentials in cybotify/.env
    ```
        mv cybotify/.env_sample cybotify/.env
        # cybotify.env
        SPOTIFY_CLIENT_ID=CLIENT_ID_HERE
        SPOTIFY_CLIENT_SECRET=CLIENT_SECRET_HERE
        SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/accounts/new/callback    # leave this
    ```

6. set your app's redirect URI to http://127.0.0.1:8000/accounts/new/callback in the spotify dashboard

6. run server
    ```
        ./manage.py runserver
    ```
