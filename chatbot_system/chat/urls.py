from django.urls import re_path
from .views import Compute

urlpatterns = [
    #path('test/', views.DemoTest.as_view()),
    # re_path('test/?$', chat_stream),
    re_path('models/chat/completions', Compute.as_view()),
]


