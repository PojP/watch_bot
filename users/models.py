from django.db import models



class Users(models.Model):
    tg_id=models.BigIntegerField(unique=True)
    username=models.CharField(max_length=100)
    referral_link=models.CharField(max_length=200,unique=True)
    referrals=models.IntegerField(default=0)
    
    ads_on=models.BooleanField(default=True)

    def __str__(self):
        return self.username

class SearchHistory(models.Model):
    user=models.ForeignKey('Users',on_delete=models.PROTECT)
    search_query=models.CharField(max_length=200)

    def __str__(self):
        return self.user

class ActiveTime(models.Model):
    user=models.ForeignKey('Users',on_delete=models.PROTECT)
    time=models.DateTimeField()

    def __str__(self):
        return self.user
