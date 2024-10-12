from django.db import models
from db_connection import db


user_collection = db['cred']

# from djongo import models

class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Remember to hash the password!

    def __str__(self):
        return self.name

