from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

from .models import FitsFile, PrimaryHDU, ExtensionHDU

@api_view(['GET'])
def index(request):
    """
    Return the number of reach kind of records.
    """
    counts = dict(FitsFile = FitsFile.objects.count(),
                  PrimaryHDU = PrimaryHDU.objects.count(),
                  ExtensionHDU = ExtensionHDU.objects.count(),
                  )
    return JsonResponse(counts)
                  
