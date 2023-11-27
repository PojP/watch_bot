from django.db import models



class Movies(models.Model):
    title=models.CharField(max_length=200)
    year=models.IntegerField(null=True)
    tg_id=models.BigIntegerField()
    rating=models.IntegerField(null=True)
