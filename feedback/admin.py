from django.contrib import admin
from .models import MartialArt, Movement, PracticeSession, ProgressHistory

admin.site.register(MartialArt)
admin.site.register(Movement)
admin.site.register(PracticeSession)
admin.site.register(ProgressHistory)
