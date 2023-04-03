from django.db import models
import random
# Create your models here.

class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to = 'uploads/team/')
    about = models.CharField(max_length=50, blank=True)

    feedback = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500)
    #links--------------------------------
    insta_url = models.CharField(blank=True, max_length=500)
    github_link = models.CharField(blank=True, max_length=500)

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all():
        return TeamMember.objects.all()


class ThrowBackImages(models.Model):
    name = models.CharField(max_length=100, default="na", blank=True)
    image = models.ImageField(upload_to = 'uploads/throwback/')

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all():
        return ThrowBackImages.objects.all()


class UtkarshEvents(models.Model):
    name = models.CharField(max_length=100)
    mini_description = models.CharField(max_length=600)
    image =  models.ImageField(upload_to = 'uploads/EventsImages/')#home screen poster.....
    body_background = models.ImageField(upload_to = 'uploads/backgrounds/') # to change background as per tabs on event.html

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all_events():
        return UtkarshEvents.objects.all()


# 3just to showw sub category of events...
"""
Exaple:

Utkarsh Events
    |
    |> Technical (UtkarshEvents Class) #just to categorize..
    |       |   
    |       |> Soft Corner (SubEvents Class) #just to categorize
    |       |       |> Di- Codifica (SubsubEvent Class) #registration on id of this....
    |
    |> Cultural  (SuvEventClass)
    |> etc...

"""

class SubEvents(models.Model):
    parent_event = models.ForeignKey(UtkarshEvents, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mini_description = models.CharField(max_length=1000)
   
    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all():
        return SubEvents.objects.all()
    @staticmethod
    def get_by_id(e):
        return SubEvents.objects.filter(parent_event_id = e)


#main event that will be diplayed as cards.. participation will be donne on the id of this...
class SubSubEvents(models.Model):
    name = models.CharField(max_length=100)
    parent_sub_event = models.ForeignKey(SubEvents, on_delete=models.CASCADE)
    image =  models.ImageField(upload_to = 'uploads/SubEventsImages/')
    mini_description = models.CharField(max_length=1000)
    descp = models.TextField(max_length=3000)

    is_team_event = models.BooleanField(default=False)

    registration_amount = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all():
        return SubSubEvents.objects.all()
    @staticmethod
    def get_by_parent_id(e):
        return SubSubEvents.objects.filter(parent_sub_event_id = e)
    @staticmethod
    def get_by_id(e):
        return SubSubEvents.objects.filter(id=e)


class RegisteredUsers(models.Model):
    uk_id = models.CharField(max_length=20, unique=True) #`utkarsh` id 
    name  = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,unique=True)
    phone = models.CharField(max_length=12)
    college_name = models.CharField(max_length=250)
    course = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    city = models.CharField(max_length=300)
    ca_refferal_code  = models.CharField(max_length=50, null=True, blank=True)

    #verifctions.......................
    # OTP = models.Intege   rField(default=0)
    # # if verified with otp status = True
    # active_status = models.BooleanField(default=False)
    
    # enrolled events....(individual)
    enrolled_events = models.ManyToManyField(SubSubEvents, blank=True)
    #ca refferal...
    is_ambassador = models.BooleanField(default=False)


    reg_fee = models.IntegerField(default=0)
    extra_charges = models.IntegerField(default=0)


    def __str__(self):
        return self.name

    @staticmethod
    def get_by_email(s):
        return RegisteredUsers.objects.filter(email=s)
    
    @staticmethod
    def get_by_id(i):
        return RegisteredUsers.objects.filter(uk_id=i)


#this is for team event 
class TeamEventRegistrations(models.Model):
    #it will be the leader if any group registration...
    team_leader_uk_id = models.CharField(max_length=50)
    event_registered = models.ForeignKey(SubSubEvents, on_delete=models.CASCADE)

    #has team...
    team_members = models.ManyToManyField(RegisteredUsers)

    fee = models.IntegerField(default=0)
    extra_charges = models.IntegerField(default=0)

    #paid True, Unpaid False
    payments_status =  models.BooleanField(default=False)

    def __str__(self):
        return self.team_leader_uk_id + "/" + self.event_registered.name
    @staticmethod
    def get_by_uk_id(tlukid):
        return TeamEventRegistrations.objects.filter(team_leader_uk_id=tlukid)
    

#CA
class CampusAmbassador(models.Model):
    ambassador_uk_id = models.CharField(max_length=20, unique=True) # store uk id
    #his refferal code....
    ambassador_id = models.CharField(max_length=50, unique=True, default=f"UKCA{random.randrange(100000,99999999)}" )
    ca_attached_persons = models.ManyToManyField(RegisteredUsers, blank=True)

    def __str__(self):
        return "Ambassador"+" "+ RegisteredUsers.get_by_id(self.ambassador_uk_id)[0].name
    @staticmethod
    def get_ca_by_uk_id(uk_id):
        return CampusAmbassador.objects.filter(ambassador_uk_id = uk_id)
    
    @staticmethod
    def get_by_ambassador_id(aid):
        return CampusAmbassador.objects.filter(ambassador_id = aid)



class Accomodation(models.Model):
    person = models.ForeignKey(RegisteredUsers, on_delete=models.CASCADE)
    amount = models.IntegerField(default=500)

    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.person.name + "/" + self.person.uk_id
    
    @staticmethod
    def get_by_person_id(pid):
        return Accomodation.objects.filter(person_id = pid)

class a(models.Model):
    name = models.CharField(max_length=20)