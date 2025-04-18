# core/models.py

from django.db import models


class Tenant(models.Model):
    student_id = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)
    db_user = models.CharField(max_length=255)
    db_password = models.CharField(max_length=255)
    db_host = models.CharField(max_length=255)
    db_port = models.CharField(max_length=255)

    def __str__(self):
        return f"""
Tenant: {self.student_id}
    api_key: {self.api_key}
        """
