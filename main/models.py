from django.db import models

class Project(models.Model):
    id = models.UUIDField(primary_key=True)
    analytics_complete = models.BooleanField(default=False)
    models_complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Column(models.Model):
    name = models.CharField(max_length=100, default=None)
    importance = models.FloatField(default=0.0)
    type = models.CharField(max_length=20, default=None)
    filled = models.FloatField(default=None)
    min = models.FloatField(default=None)
    mean = models.FloatField(default=None)
    median = models.FloatField(default=None)
    max = models.FloatField(default=None)
    unique = models.IntegerField(default=None)
    target = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.project) + ": " + self.name


class Model(models.Model):
    name = models.CharField(max_length=40, default=None)
    accuracy = models.FloatField(default=0.0)
    roc = models.FloatField(default=0.0)
    f1 = models.FloatField(default=0.0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.project) + ": " + self.name
