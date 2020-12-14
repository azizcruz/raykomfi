from .models import Message, ImportantAdminMessages
from django.db.models import Q

def not_opened_messages(request):
    data = {}
    if request.user.is_authenticated:
        not_opened_messages = Message.objects.filter(Q(receiver=request.user) & Q(is_read=False)).prefetch_related('user', 'receiver')
        data['not_opened_messages'] = not_opened_messages
    if ImportantAdminMessages.objects.filter(show=True).exists():
        message = ImportantAdminMessages.objects.filter(show=True).first()
        data['important_message'] = message.message
    return data