# Installation the server

Run all commands inside the `src` directory.

```shell
python -m venv src/venv
source src/venv/bin/activate
pip install -r src/requirements.txt
```

# Set up the server
```shell
cp src/.env.example src/.env
```

Then modify it.

```shell
python src/manage.py migrate
python src/manage.py createsuperuser
```

# Get started the server

Cron:
```shell
python src/manage.py manage_sectors
```

Running the server:
```shell
python src/manage.py runserver
```