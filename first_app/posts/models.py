from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    image = models.ImageField(upload_to='media/')
    body = models.TextField()

    def __str__(self):
        return self.title

    def summary(self):
        return self.body[:40]