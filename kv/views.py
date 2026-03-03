import json

import redis
from django.conf import settings
from django.http import JsonResponse

r = None


def get_redis():
    global r
    if r is None:
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return r


def root(request):
    return JsonResponse(
        {
            "routes": [
                {"method": "GET", "path": "/kv/{key}", "description": "Get a value by key"},
                {"method": "PUT", "path": "/kv/{key}", "description": "Set a value by key"},
                {
                    "method": "DELETE",
                    "path": "/kv/{key}",
                    "description": "Delete a value by key",
                },
            ]
        }
    )


def kv(request, key):
    if request.method == "PUT":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        if "value" not in body:
            return JsonResponse({"error": "Missing 'value' in request body"}, status=400)
        get_redis().set(key, body["value"])
        return JsonResponse({"key": key, "value": body["value"]})

    if request.method == "GET":
        value = get_redis().get(key)
        if value is None:
            return JsonResponse({"error": "Key not found"}, status=404)
        return JsonResponse({"key": key, "value": value})

    if request.method == "DELETE":
        if not get_redis().delete(key):
            return JsonResponse({"error": "Key not found"}, status=404)
        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)
