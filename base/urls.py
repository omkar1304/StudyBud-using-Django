from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutPage, name='logout'),

    path('user-profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('update-profile', views.updateUser, name='update-profile'),


    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),

    path('room-form/', views.createRoom, name='room-form'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),

    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),


    path('browse-topics/', views.browseTopics, name='browse-topics'),
    path('activity/', views.activity, name='activity'),
    

]
