from django.shortcuts import render

from django.http import HttpResponse


def warmup():
    return HttpResponse(status=200)
