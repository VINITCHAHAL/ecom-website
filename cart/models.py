from django.db import models
from db_connection import db
user_collection = db['cred']

class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

