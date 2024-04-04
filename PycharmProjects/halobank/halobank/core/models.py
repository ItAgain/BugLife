from django.db import models


class Operation(models.Model):
    card_id = models.IntegerField()
    amount = models.IntegerField()
    shop = models.CharField(max_length=256)
    date = models.DateTimeField()
