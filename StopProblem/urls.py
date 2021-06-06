"""StopProblem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from stop_problem import views as app_views

urlpatterns = [
    path('', app_views.PlayerRegistrationView.as_view(), name='player-registration'),
    path('start-game/', app_views.StartGameView.as_view(), name='start-game'),
    path('game/', app_views.GameSequenceView.as_view(), name='game'),
    path('thanks-for-playing/', app_views.ThanksForPlayingView.as_view(), name='thanks-for-playing'),
    path('admin/', admin.site.urls),
]
