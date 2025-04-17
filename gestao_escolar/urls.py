from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # 👈 Import necessário

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alunos/', include('alunos.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('controle/', include('controle.urls')),
    
]

# 👇 Adicione isso para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
