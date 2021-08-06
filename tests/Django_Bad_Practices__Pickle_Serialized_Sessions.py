SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

from django.contrib.sessions import serializers
from django.core import signing

signing.loads(value, serializer=serializers.PickleSerializer)