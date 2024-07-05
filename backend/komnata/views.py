from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class HomeView(APIView):
   permission_classes = (IsAuthenticated, )
   def get(self, request):
       content = {'message': f'Welcome to the JWT Authentication page using React Js and Django {request.user}!'}
       return Response(content)
