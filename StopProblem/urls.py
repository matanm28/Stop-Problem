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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from stop_problem import views as app_views

urlpatterns = [
                  path('', lambda req: redirect('start-game')),
                  path('start-game/', app_views.StartGameView.as_view(), name='start-game'),
                  path('player-registration', app_views.PlayerRegistrationView.as_view(), name='player-registration'),
                  path('game-sequence/', app_views.GameSequenceView.as_view(), name='game-sequence'),
                  path('thanks-for-playing/', app_views.ThanksForPlayingView.as_view(), name='thanks-for-playing'),
                  path('about/', app_views.AboutView.as_view(), name='about'),
                  path('admin/', admin.site.urls),
              ]
