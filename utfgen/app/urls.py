from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('professor/', views.professor, name="professor"),
    path('disciplina/', views.disciplinas, name="disciplina"),
    path('getTimeAvaliable/<uuid:id>/', views.getTimeAvaliable, name="getTimeAvaliable"),
    path('deleteTimeAvaliable/<uuid:id>/', views.deleteTimeAvaliable, name="deleteTimeAvaliable"),
    path('getSubject/<uuid:id>/', views.getSubject, name="getSubject"),
    path('editSubject/<uuid:id>/', views.editSubject, name="editSubject"),
    path('registerTime/', views.registerTime, name="registerTime"),
    path('genetic/', views.genetic, name="genetic")
]