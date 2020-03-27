from django.db import models

class Port(models.Model):
    port_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'port'


class Port1(models.Model):
    port_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'port1'

class Test1(models.Model):
    no = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=32)
    port_num = models.CharField(max_length=32)
    state = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'test1'