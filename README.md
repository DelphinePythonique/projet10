# projet10
## Goals: 
Create a secure RESTful API using Django REST to manage projects and there issues.

version: 1.0.0

## Summary

[Install](#install)

[Use](#use)

[Todo](TODO.md)

[Changelog](CHANGELOG.md)

------------
### <a name="install"></a>Install

This setup is for a development environment.

Prerequisite:

- \>= python3,9

Through a terminal(Debian linux) or Powershell(Windows) : 

Position yourself in the local directory in which you want to position the sources of the application
``` bash
 cd [path_to_source_directory]
```
-  Clone the repository via the clone command in ssh mode
[ssh](https://docs.github.com/en/authentication/connecting-to-github-with-ssh), via la commande suivante

``` bash
 git clone git@github.com:DelphinePythonique/projet10.git
```

- Position yourself in the project directory, create a virtual environment

``` bash
 cd projet10
 python -m venv env
```
- Activate virtual environment

   If OS is Debian Linux: 
``` bash
 source env/bin/activate
```
   If OS is Windows:
``` bash
 .\env\Scripts\activate
```
- Install dependencies
``` bash
 pip install -r requirements.txt
```
- Install dev dependencies
``` bash
 pip install -r requirements_dev.txt
```

- In the settings's file change key's values , for example
``` python
 SECRET_KEY = "django-insecure-ceciestmasecretkeymouahahh"
 DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
- in terminal, go to in directory which containing manage.py
- if you do not want to use the default database, you can: 
  - generate database and populate it
  - create superuser -> answer questions
``` bash
 python manage.py migrate --run-syncdb
 python manage.py createsuperuser 
```
- start development server 
``` bash
 python manage.py runserver 8000 
```
- generate the flake8-html report
``` bash
  flake8 --format=html --htmldir=flake-report --exclude=env
```
- in terminal, go to in directory which containing manage.py
- generate open api file to import in postman
``` bash
python manage.py generateschema  --file project/schema.yaml --title "softdesk Api"

```

### <a name="use"></a>Uses

[API documentation](https://documenter.getpostman.com/view/11542998/2s8YeixG3R)
