import base64
from django.contrib import admin
from django.urls import include, path, re_path
from django.shortcuts import redirect


def short_link_redirect(request, encoded_id):
    """Редирект с короткой ссылки на страницу рецепта во фронтенде."""
    try:
        padded_id = encoded_id + '=' * (-len(encoded_id) % 4)
        decoded_id = base64.urlsafe_b64decode(padded_id.encode()).decode()
        recipe_id = int(decoded_id)
    except Exception:
        # Можно редиректить на главную, если ссылка битая
        return redirect('/')
    return redirect(f'/recipes/{recipe_id}/')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    re_path(r'^s/(?P<encoded_id>[^/]+)/$', short_link_redirect),
]
