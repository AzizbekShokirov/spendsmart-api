<br/>
<div align="center">

<h3 align="center">SpendSMART</h3>
<p align="center">
API for personal finance management application


  


</p>
</div>

 ### Built With
- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)

 ### Installation
1. Clone the repo
   ```sh
   git clone https://github.com/AzizbekShokirov/SpendSmart/tree/backend
   ```
2. Install packages
   ```sh
   pip install -r reqirements.txt
   ```
3. Configure your .env file in project directory 'backend'
   ```sh
   # Django configuration
   SECRET_KEY = 'your_secret_key'  #see in setting.py
   DEBUG = True or False
   ```
   ```sh
   # JWT configuration
   ACCESS_TOKEN_LIFETIME = integer number (minutes) 
   REFRESH_TOKEN_LIFETIME = integer number (days)  
   ROTATE_REFRESH_TOKENS = True
   BLACKLIST_AFTER_ROTATION = True
   ```
   ```sh
   # PostgreSQL Database configuration
   DB_HOST=hostname
   DB_NAME=database name
   DB_USER=username
   DB_PASSWORD=password
   DB_PORT=port
   ```
3. Run commands:
   ```sh
   python manage.py makemigrations
   ```
   ```sh
   python manage.py migrate
   ```
   ```sh
   python manage.py runserver
   ```
