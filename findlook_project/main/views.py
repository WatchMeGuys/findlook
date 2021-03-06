from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from . import models
from .forms import (SuggestionForm, UserLoginForm, UserProfileInfoForm, UserForm)
from django.forms import model_to_dict
import json
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, ListView, DetailView, View
# generics - классы для представления DRF.
from rest_framework import generics
# APIview стоит во главе иерархии всех классов представления DRF. 
# ListView наследуется от APIView 
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from typing import List, Dict
from .ex_handler import ExceptionResolver as ER
# Create your views here.



class IndexView(TemplateView):
    template_name = 'main/main.html'
    def get_context_data(self, **kwargs: any) -> Dict[str, any]:
        context = super().get_context_data(**kwargs)
        # Edit context if needed.
        return context

class AboutView(TemplateView):
    template_name = 'main/about.html'
    def get_context_data(self, **kwargs: any) -> Dict[str, any]:
        return super().get_context_data(**kwargs)
        

# class WebpageListView(ListView):
#     model = models.Webpage
#     context_object_name = 'webpages'
#     template_name = 'main/main.html'


# class WebpageDetailView(DetailView):
#     model = models.Webpage
#     template_name = 'main/detail.html'
#     context_object_name = 'webpage_detail'



class SuggestionView(View):
    suggestion_form = SuggestionForm
    template_name = 'main/suggestion.html'
    validation_dict = {'success': None}
    
    def get(self, request):
        form = self.suggestion_form
        return render(request, self.template_name,
                      {'suggestion_form': form})

    def post(self, request):
        form = self.suggestion_form(request.POST)
        if form.is_valid():
            form.save()
            self.validation_dict['success'] = True
        else:
            self.validation_dict['success'] = False
        return HttpResponse(json.dumps(self.validation_dict))


class RegistrationView(View):
    template_name = 'main/registration.html'
    user_form = UserForm
    profile_form = UserProfileInfoForm

    def get(self, request):

        context = {
            'user_form': self.user_form,
            'profile_form': self.profile_form,    
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        ERROR = False
        user_form = self.user_form(data=request.POST)
        profile_form = self.profile_form(data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            # Get clean form data.
            user = user_form.save(commit=False)
            try:
                validate_password(user.password, user)           
                # Hash the password.
                user.set_password(user.password)
                # Save that hash.
                user.save() 
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            except Exception as e:
                ERROR = True
        else:
            print(user_form.errors, profile_form.errors)
            ERROR = True
        return HttpResponse(json.dumps({'error': ERROR}))



class UserLoginView(View):
    login_form = UserLoginForm
    template_name = 'main/login.html'

    def get(self, request):
        return render(request, self.template_name, {'login_form': self.login_form})
    
    def post(self, request):
        login_form = self.login_form(request.POST)
        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data['username'],
                                password=login_form.cleaned_data['password'])
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponse(json.dumps({'Error':True,'ErrorCode':'UserNotActive'}))
            else:
                return HttpResponse(json.dumps({'Error':True, 'ErrorCode':'Data is not correct'}))
        else:
            return HttpResponse(json.dumps({'Error':True, 'ErrorCode': 'Data is not valid'}))


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))



# class UserSuggestionAPIView(generics.ListAPIView):
#     queryset = models.UserSuggested.objects.all()
#     serializer_class = UserSerializer

class UserSuggestionAPIView(APIView):
    def get(self, request):
        data = models.UserSuggested.objects.all()
        # Response function translate dictionary into json string.
        return Response({'names':data.values('name')})

    def post(self, request):
        post_new = models.UserSuggested.objects.create(
            name = request.data['name'],
            email = request.data['email'],
            message = request.data['message'],
        )
        return Response({'post': model_to_dict(post_new)})
