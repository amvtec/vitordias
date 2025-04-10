from django.contrib import admin
from .models import Setor, Funcionario, HorarioTrabalho, Feriado, FolhaFrequencia
from .models import SabadoLetivo
from .models import Escola

admin.site.register(Setor)
admin.site.register(Funcionario)
admin.site.register(HorarioTrabalho)
admin.site.register(Feriado)
admin.site.register(FolhaFrequencia)
admin.site.register(SabadoLetivo)
admin.site.register(Escola)