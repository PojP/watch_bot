from django.db import models
import django.utils.timezone as tz

class Users(models.Model):
    tg_id=models.BigIntegerField(unique=True)
    username=models.CharField(max_length=100)
    referral_link=models.CharField(max_length=200,unique=True,null=False)
    referrals=models.IntegerField(default=0)
    
    ads_on=models.BooleanField(null=False,default=True)

    def __str__(self):
        return self.username

class AutoPost(models.Model):
    post_id=models.BigIntegerField(unique=True)
    time=models.DateTimeField(default=tz.now)
    amount_of_users=models.IntegerField(null=False,default=0)


class SearchHistory(models.Model):
    user=models.ForeignKey('Users',on_delete=models.PROTECT)
    search_query=models.CharField(max_length=200)
    was_found=models.BooleanField(default=False)
    def __str__(self):
        return self.user

class ActiveTime(models.Model):
    user=models.ForeignKey('Users',on_delete=models.PROTECT)
    time=models.DateField(default=tz.now)

    def __str__(self):
        return self.user
