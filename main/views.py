import os
import pandas as pd
import threading

from django.shortcuts import redirect, render
from modules import analysis_engine
from rest_framework import generics
from .models import Project, Column, Model
from .serializers import ProjectSerializer, ColumnSerializer, ModelSerializer

class GetProjectInfo(generics.ListAPIView):
    """
    Provides a get method handler for project information.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(id=self.kwargs['id'])


class GetColumnInfo(generics.ListAPIView):
    """
    Provides a get method handler for column information.
    """
    serializer_class = ColumnSerializer

    def get_queryset(self):
        return Column.objects.filter(project=self.kwargs['id'])


class GetModelInfo(generics.ListAPIView):
    """
    Provides a get method handler for model information.
    """
    serializer_class = ModelSerializer

    def get_queryset(self):
        return Model.objects.filter(project=self.kwargs['id'])


def upload_view(request):

    if 'myfile' in request.FILES:
        new_project = analysis_engine.create_project()
        analysis_engine.run(new_project, request.FILES['myfile'])
        return redirect('/project/' + str(new_project.id))

    return render(request, 'upload.html')


# Create your views here.
def index(request, id):

    host = request.get_host()
    print('Host:', host)
    if host == '0.0.0.0:8000':
        host = 'http://' + host
    else:
        host = 'https://' + host

    proj = Project.objects.get(id=id)
    if proj.models_complete == False:
        return render(request, 'loading.html', {'id': id, 'host': host})

    return render(request, 'main.html', {'id': id, 'host': host})
