# urls.py
from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('', lambda request: redirect('index', permanent=False)),
    path('home/', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('ngo-dashboard/', views.ngoDashboard, name="ngo-dashboard"),
    path('investor-dashboard/', views.investorDashboard, name="investor-dashboard"),
    path('fundraiser-dashboard/', views.fundraiserDashboard, name="fundraiser-dashboard"),
    path('logout/', views.logout, name='logout'),
    path('fundraiser-create-post/', views.fundraiserCreatePost, name="fundraiser-create-post"),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/invest/', views.invest, name='invest'),
    path('ngo-create-post/', views.ngo_create_post, name="ngo-create-post"),  # New path
    path('donation-post/<int:pk>/', views.donation_post_detail, name='donation_post_detail'),
    path('donation-post/<int:pk>/donate/', views.donate, name='donate'),
    path('success-stories/', views.success_stories, name='success_stories'),
    path('our-mission/', views.our_mission, name='our_mission'),
    path('careers/', views.careers, name='careers'),
    path('team/', views.team, name='team'),
]