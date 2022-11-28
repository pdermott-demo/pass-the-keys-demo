# Pass the keys technical test

### By Pete Dermott
#### peterdermott@fastmail.com

---
### Installation
The app is built with the following os packages:
- Python 3.8.10
- Postgres 14.3
- Redis server 5.0.7 (for celery tasks - optional)

Once these packages are installed and available the application can be installed into a virtualenv environment
using the following command:
`pip install -r requirements.txt`

The database configuration uses the dj-database-url package, this means you can set a new database by either 
adding a `DATABASE_URL` environment variable or by editing the `DATABASES` variable in pass_the_keys_demo/settings.py

### Database population
There is a management command provided to fetch the csv file and make the appropriate requests to the postcodes.io API.
This command can be run using `python manage.py fetch_data_from_airbnb`

#### Celery tasks
The fetching of the outcode data is performed in celery tasks to improve performance.
To start a celery worker run `celery -A pass_the_keys_demo worker -l info`

This is optionally disabled by uncommenting the `CELERY_ALWAYS_EAGER=True` line in the pass_the_keys_demo/settings.py 
file.

### Testing
Tests can be run in the usual manner via `python manage.py test` coverage is currently 93%, I had hoped to get this to 
100%, sadly I ran out of time.

---
Thank you for your time on this so far, I look forward to discussing this work and potential improvements in an
upcoming interview.

