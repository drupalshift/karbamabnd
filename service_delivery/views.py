from django.shortcuts import render
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):

    template_name = "index.html"


class AboutUsView(TemplateView):

    template_name = "about_us.html"


class TermsConditionsView(TemplateView):

    template_name = "terms_and_conditions.html"