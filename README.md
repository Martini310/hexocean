
# Hexocean recruitment task
## Try it!
The app is deployed and is running live on *Render*, you can try it on:
[https://hex-drf.onrender.com/admin](https://hex-drf.onrender.com/admin)

```
*passes to admin*
username: admin
password: admin
```
**Due to the free plan the first access may take some time before the server wakes up.** <br>
*The only limitation of this solution is that there is an issue with providing static files. Unfortunately I haven't had time to learn how to connect this with AWS or something similar*


### or
## Run app locally

To start the app locally first you need to get the project:

```
git clone https://github.com/Martini310/hexocean.git
``` 
Then you need to install requirements
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

## Alternatively you can run the app using *docker-compose.yaml*

It's just a few steps <br>
In project root directory run:
```
docker-compose up -d --build
```
Next, run migrations:
```
docker-compose exec web python manage.py migrate
```
And create super user:
```
docker-compose exec web python manage.py createsuperuser
```
#### And that's it! You can access the app on [0.0.0.0:8000/admin]() or [localhost:8000/admin]()

### Additional info
* If you want to use POSTMAN to test the app (which I recommend) to authenticate the user set username and password in Authorization card > Type 'Basic Auth'
* I made a decission to not create a new user model nor modify the default, I just created OneToOneField to assign a Tier to user this way
* You need to add prefix with hostname to download image link from response. I didn't found the good and straightforward solution to make it dynamic and not to hard code that.
* I also cannot find a way to delete images created after run **pytest**
* API documentation in SwaggerUI is available under [localhost:8000/schema/docs]()
