from .models import Message
from django.db.models import Q

def not_opened_messages(request):
    if request.user.is_authenticated:
        not_opened_messages = Message.objects.filter(Q(receiver=request.user) & Q(is_read=False))
        return {'not_opened_messages': not_opened_messages}
    return {}