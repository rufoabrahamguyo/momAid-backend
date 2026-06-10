from django.http import JsonResponse


def welcome_view(request):
    return JsonResponse({"detail": "API is up."})
