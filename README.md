# Security Force Monitor: Backend

## OS Level dependencies

* Python 3.5
* PostgreSQL 9.4+ 
* PostGIS
* osm2pgsql

## Development

    mkvirtualenv sfm
    git clone git@github.com:security-force-monitor/sfm-cms.git
    cd sfm/sfm_pc

Install the requirements:

    pip install -r requirements.txt

Create a database:

    createdb sfm-db
    psql sfm-db -c "CREATE EXTENSION postgis;"
    export DATABASE_URL=postgis://localhost/sfm-db
    ./manage.py migrate --noinput

Load static data:

```
# Load fixtures for Violation Types and Organization classification types
./manage.py loaddata violation_types
./manage.py loaddata classification_types

# Load Geonames data
./manage.py import_geonames
./manage.py update_countries_plus
```

Create search index and 

# Create Materialized Views for global search and looking up a Geoname object
# based upon a geoname id 
./manage.py make_search_index

Create an admin user:

    ./manage.py createsuperuser

Start the web server:

    ./manage.py runserver

Open http://127.0.0.1:8000/ and sign in with your email and password.
