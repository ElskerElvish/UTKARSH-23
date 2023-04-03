from django.contrib import admin
from . import models
from django.conf import settings
import random
import csv
from django.http import HttpResponse

admin.site.site_header = 'UTKARSH\'23 Administration'


@admin.action(description="Export")
def export(modeladmin, request, queryset):
    with open(settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/temp.csv', "w", newline="") as f:
        queryset = queryset.values()
        w = csv.DictWriter(f, queryset[0].keys())
        w.writeheader()
        for each in queryset:
            w.writerow(each)

    with open(settings.MEDIA_ROOT / 'UtkarshWebsite/static/deliver/temp.csv', "r") as f:
        resp = HttpResponse(f.read(), content_type='text/csv')
        return resp


@admin.action(description="Export Registered Users")
def exportRegUsers(modeladmin, request, queryset):
    def getEvents(l):
        n = ''
        for t in l:
            n += t.name + ', '
        if n:
            return n
        else:
            return "Empty"

    headers = ["UK id","Name","Email","Phone","College","Course","Gender","City","Events Enrolled"]
    with open(settings.MEDIA_ROOT / 'UtkarshWebsite/static/deliver/temp.csv', "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)

        for each in queryset.order_by('college_name'):
            ev = getEvents(each.enrolled_events.all())
            to_write = [
                each.uk_id, each.name, each.email, each.phone, each.college_name, each.course,each.gender ,each.city, ev
            ]
            w.writerow(to_write)

    with open(settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/temp.csv', "r") as f:
        resp = HttpResponse(f.read(), content_type='text/csv')
        resp['Content-Disposition'] = "attachment; filename=UserRegistrations.csv " 
        return resp

class RegisteredUsersAdmin(admin.ModelAdmin):
    list_display = ["uk_id","name","college_name","email","enrolled_eventssss"]
    list_filter = ('college_name',)
    search_fields = ("name", "uk_id","phone")

    actions = [exportRegUsers,]

    def enrolled_eventssss(self, obj):
        n = ''
        for i in obj.enrolled_events.all():
            n += i.name+','
        if n:
            return n
        else:
            return "Empty"
        # for each in obj.enrolled_events:
            
    enrolled_eventssss.short_description = 'Enrolled Events'
    # enrolled_eventssss.empty_value_display = 'Not Available'

class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    actions = [export,]

class ThrowBackImagesAdmin(admin.ModelAdmin):
    list_display = ["name"]


class UtkarshEventsAdmin(admin.ModelAdmin):
    list_display = ["name","mini_description"]
    actions = [export, ]


class SubEventsAdmin(admin.ModelAdmin):
    list_display = ["name","parent_event","mini_description"]
    actions = [export]




class SubSubEventsAdmin(admin.ModelAdmin):
    list_display = ["name","parent_sub_event"]
    search_fields = ("name","parent_sub_event__name")
    list_filter = ("name","parent_sub_event__name","parent_sub_event__parent_event__name")




class EventRegistraionsAdmin(admin.ModelAdmin):
    list_display = ["user_id",""]


def get_team_leader_name(i):
    ru = models.RegisteredUsers.get_by_id(i.upper())[0]
    return (ru.name, ru.phone, ru.college_name)

@admin.action(description="Export Team Registration")
def exportTeam(modeladmin, request, queryset):
    
    def getTeam(l):
        n = ''
        for t in l:
            n += f"{t.name} ({t.uk_id})" + ', '
        if n:
            return n
        else:
            return "Empty"

    headers = ["Team Leader","Phone","College","Event","Team Members"]
    with open(settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/temp.csv', "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)

        for each in queryset.order_by('team_leader_uk_id'):
            tl = get_team_leader_name(each.team_leader_uk_id)
            teamMembers = getTeam(each.team_members.all())
            to_write = [
                tl[0], tl[1], tl[2], each.event_registered.name, teamMembers
            ]
            
            w.writerow(to_write)

    with open(settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/temp.csv', "r") as f:
        resp = HttpResponse(f.read(), content_type='text/csv')
        resp['Content-Disposition'] = "attachment; filename= TeamEventRegistrations.csv "
        return resp

class TeamEventRegistrationsAdmin(admin.ModelAdmin):
    list_display = ["teamLeader","regs","Team"]
    search_fields = ("team_leader_uk_id","team_leader_uk_id")
    actions = [exportTeam, ]

    def teamLeader(self, obj):
        tl = get_team_leader_name(obj.team_leader_uk_id)
        return tl[0]+'/'+tl[2]

    def Team(self,obj):
        n = ""
        for i in obj.team_members.all():
            n += i.name+", "
        return n

    def regs(self, obj):
        return obj.event_registered.name    
    
    regs.short_description = "Registrations"
    teamLeader.short_description = "Team Leader"


class CampusAmbassadorAdmin(admin.ModelAdmin):
    list_display = ["ambassador_uk_id","ambassador_id", "Refferals"]
    search_fields = ("ambassador_uk_id","ambassador_id")


    def Refferals(self, obj):
        n = ''
        for i in obj.ca_attached_persons.all():
            n += i.name + ", "
        if n:
            return n
        else:
            return "No Refferals"
    

@admin.action(description="Export Accomodation")
def exportAcco(modeladmin, request, queryset):
    headers = ["Utkarsh id", "Name","Gender","Phone","Email","College","City", "Fee"]
    with open(settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/temp.csv', "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)

        for each in queryset.order_by('person__name'):
            to_write = [
                each.person.uk_id, each.person.name,each.person.gender , each.person.phone, each.person.email, each.person.college_name, each.person.city, each.amount
            ]
            w.writerow(to_write)

    with open(settings.MEDIA_ROOT / 'UtkarshWebsite/static/deliver/temp.csv', "r") as f:
        resp = HttpResponse(f.read(), content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename=Accomodation.csv'
        return resp

class AccomodationAdmin(admin.ModelAdmin):
    list_display = ["person","amount","paid"]
    search_fields = ("person",)

    actions = (exportAcco, )


admin.site.register(models.Accomodation, AccomodationAdmin)
admin.site.register(models.CampusAmbassador, CampusAmbassadorAdmin)
admin.site.register(models.TeamEventRegistrations, TeamEventRegistrationsAdmin)
admin.site.register(models.SubSubEvents, SubSubEventsAdmin)
admin.site.register(models.SubEvents , SubEventsAdmin)
admin.site.register(models.UtkarshEvents, UtkarshEventsAdmin)
admin.site.register(models.ThrowBackImages, ThrowBackImagesAdmin)
admin.site.register(models.TeamMember, TeamAdmin)
admin.site.register(models.RegisteredUsers, RegisteredUsersAdmin)