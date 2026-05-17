import datetime
from django.utils import timezone
from redis.exceptions import ResponseError
from django.http import JsonResponse
from mumaid.utils.discord import send_error_to_discord

class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Django automatically catches any unhandled view exception here.
        """
        message_err = str(exception).lower()
        

        user_email = request.user.email if request.user and request.user.is_authenticated else "Anonymous User"


        if isinstance(exception, ResponseError) and "max daily request limit exceeded" in message_err:
            return self.redis_maintenance(request, user_email)

        discord_payload = {
            "Error": message_err,
            "Path": request.path,
            "User": user_email,
        }
        
        send_error_to_discord(discord_payload)

        return None

    def redis_maintenance(self, request, user_email):
        """
        Helper method to structure the Redis downtime response.
        """
        now_utc = timezone.now()
        
        estimated_back_online = now_utc + datetime.timedelta(minutes=45)

        response_data = {
            "status": "maintenance",
            "message": "Server temporarily down for database optimization.",
            "estimated_time": estimated_back_online.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


        discord_alert = {
            "Alert": "⚠️ REDIS QUOTA EXHAUSTED",
            "Path": request.path,
            "User": user_email,
            "Message": "Upstash free tier limit reached. Sent maintenance screen to mobile client."
        }
        send_error_to_discord(discord_alert)

        return JsonResponse(response_data, status=503)