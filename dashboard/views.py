from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

def index(request):
    if request.user.is_authenticated:
        User = get_user_model()
        users = User.objects.all()

        contenxt = {
            "username": request.user,
            "users_count": len(users),
        }
        return render(request, "dashboard/index.html", contenxt)
    return redirect('/access')
