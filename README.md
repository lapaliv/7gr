# Installation the server

Run all commands inside the `server` directory.

```shell
python -m venv server/venv
source server/venv/bin/activate
pip install -r server/requirements.txt
```

# Set up the server
```shell
cp server/.env.example server/.env
```

Then modify it.

```shell
python server/manage.py migrate
python server/manage.py createsuperuser
```

# Get started the server

Cron:
```shell
python server/manage.py manage_sectors
```

Running the server:
```shell
python server/manage.py runserver
```