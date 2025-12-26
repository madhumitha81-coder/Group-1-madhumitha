from django.contrib import admin
from .models import Task, Project, Proposal, Contract, Message, Review, Profile, Skill  # remove Freelancer

admin.site.register(Task)
admin.site.register(Project)
admin.site.register(Proposal)
admin.site.register(Contract)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Profile)
admin.site.register(Skill)
