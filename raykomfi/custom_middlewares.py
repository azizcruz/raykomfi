from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from dateutil.parser import parse

from django.core.cache import cache 
from django.conf import settings

from .models import User

class AutoLogout(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Can't log out if not logged in
            return self.get_response(request)

        try:
            if request.user.stay_logged_in == False and datetime.now() - parse(request.session['last_touch']) > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                try:
                    auth.logout(request)
                    del request.session['last_touch']
                except KeyError:
                    print('Error: Keyerror in middleware for auto logout')
                else:
                    request.session['last_touch'] = datetime.now().isoformat()
        except:
            request.session['last_touch'] = datetime.now().isoformat()

        return self.get_response(request)