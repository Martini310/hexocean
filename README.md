# hexocean
pytest --ds=core.settings
../manage.py spectacular --file schema.yaml

# Hexocean recruitment task
### Try it!
The app is deployed and is running live on *Render*, you can try it on:
[render](http://127.0.0.1:8000/admin)

```
*passes to admin*
username: admin
password: admin
```

### or
### Run app locally

To start the app locally first you need to get the project:

```
git clone ...
``` 
First of all you need to install requirements
```
pip install -r requirements.txt
```
Once you have a repo and all dependencies, it is time to make migrations <br>
In root directory of the app run:
```
python manage.py makemigrations
```
Next:
```
python manage.py migrate
```
Before we start the server, let's create a super user
```
python manage.py createsuperuser
```
Set username, email and password for your super user and then run the server:
```
python manage.py runserver
```

The app have a preloaded data (user tiers and thumbnail sizes) the only thing needed to be done is to assign our user to proper tier.<br>
Go to [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and create new *Profile*. It is simply, just select user and designed tier.

### Alternatively you can run the app using *docker-compose.yaml*


