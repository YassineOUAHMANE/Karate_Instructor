from django.views.generic import TemplateView, DetailView
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from feedback.models import MartialArt

class HomeView (TemplateView) :
    template_name = 'show/index.html'

class AboutView (TemplateView) :
    template_name = 'show/about.html'

class ContactView (TemplateView) :
    template_name = 'show/contact.html'

def contact_view(request) :
    if request.method == "POST" : 
        if "submission" in request.POST : 
            send_mail(
            request.POST["subject"],
            "This email is from : " + request.POST["name"] + "\n" + request.POST["content"],
            request.POST["email"],  
            ['yassiraamoud1@gmail.com'],
            fail_silently=False
        )
            return redirect('contact')
    render(request=request, template_name="show/contact.html")

def programs_view (request):
    martial_arts = MartialArt.objects.all()
    return render(request=request, template_name='show/programs.html', context= { "martial_arts" : martial_arts}) 

class TeamView (TemplateView) : 
    template_name = 'show/team.html'