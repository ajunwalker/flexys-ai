from rest_framework import serializers
from .models import Project, Column, Model


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "analytics_complete", "models_complete")


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ("name", "type", "filled", "min", "mean", "median", "max",
                  "unique", "target", "importance")


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ("name", "accuracy", "f1", "roc")
