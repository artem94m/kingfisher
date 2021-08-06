from django.http.response import JsonResponse as jr

response = jr(sensitive_data, safe=False)

response = jr(sensitive_data, safe=0)