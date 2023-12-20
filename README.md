## Liiga stats by roopeh
#### Powered by Django, HTML, Javascript

My version of Finnish hockey league Liiga's website where you can find previous and
upcoming games. You can also see current team standings and player stats.

You may sort player stats by goals, assists or points. You can also filter games and
players in player stats by selecting a team from top bar.

[**Live demo**](https://liiga-app-2023.fly.dev/)<br/>

### How to install your own copy
You need Python installed. Activate virtual environment with `pipenv shell` and
run `pipenv install`

Next collect static files by `python manage.py collectstatic` and finally you
can run server with `python manage.py runserver`

Now you may browse Liiga app at http://localhost:8000/
