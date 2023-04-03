from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from .models import RegisteredUsers, TeamMember, ThrowBackImages, UtkarshEvents, SubEvents, SubSubEvents, TeamEventRegistrations, CampusAmbassador,Accomodation
from django.conf import settings
from .import sendmail
import random
import re

REGISTRATIONS_ON = True
PAYMENT_DISCLAIMER = """

The Registration fee for pariticipation is Rs. 1000/- .
(i.e. You will have to pay 1000 if you participate in any one or more events inside Techincal category or any other category *EXCEPT SPORTS* ) 
 For sports activities, registration and fees will be accepted on-site and will be handled
per event.

"""
def verifyEmail(email):
	if(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)):
		return True
	else:
		return False


def sendOTP(email, name, otp, uk_id):
    # obj = 
    try:
        obj = "Utkarsh Registration OTP"
        body = f"Dear {name} kindly use {otp} as your one time verification"
        mail = sendmail.SendEmail(settings.PROVIDER, settings.OUR_EMAIL)
        auth = mail.gmail_authenticate()
        mail.send_message(auth, destination, obj, body)
    except Exception as e:
        print(e)



# Create your views here.
def home(request):
    if request.method == 'GET':
        ru = None
        tm = TeamMember.get_all()
        tb =  ThrowBackImages.get_all()
        evs = UtkarshEvents.get_all_events()[:4]

        if request.user.is_authenticated:
            
            ru = RegisteredUsers.get_by_id(request.user.username)[0]
            enrolled_events =  ru.enrolled_events.all()

            tevr = TeamEventRegistrations.get_by_uk_id(ru.uk_id)
            # enrolled_events = EventRegistraions.get_by_uk_id(request.user.username)

            #fetch accomodaiton details...
            accomodation_details = Accomodation.get_by_person_id(ru)

            ambassador_data = ''
            if ru.is_ambassador:
                ambassador_data = CampusAmbassador.get_ca_by_uk_id(ru.uk_id)[0]
                ambassador_data = ( ambassador_data.ca_attached_persons.all(), ambassador_data)


            payments = 0
            summary = {}
            p = ["sports","informal"]
            for i in enrolled_events:
                c =  i.parent_sub_event.parent_event.name
                if c.lower() in p:
                    summary[i.name] = i.registration_amount
                    payments += i.registration_amount

            for j in tevr:
                c =  j.event_registered.parent_sub_event.parent_event.name
                if c.lower() in p:
                    summary[j.event_registered.name] = j.event_registered.registration_amount
                    payments += j.event_registered.registration_amount

            if accomodation_details:
                summary["Accomodation"] = accomodation_details[0].amount
                payments += accomodation_details[0].amount

            summary["Total"] = payments

            return render(request,'home.html', {"payments":summary,"ru":ru,"team":tm,"throwback":tb,"events":evs,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"tevr":tevr,"accomodation_details":accomodation_details})
            # else:
            #     #if otp is not verified...
            #     print("User not verified...")
            #     sendOTP(email, name, otp, ukid)
            #     return JsonResponse()
        else:
            return render(request,'home.html', {"team":tm,"throwback":tb,"events":evs})

def generateUtkarshId():
    uk_id = f"UK{random.randrange(1000, 9999)}"
    while True:
        #check if id alresy exists or not
        d = RegisteredUsers.get_by_id(uk_id)
        if not d:
            return uk_id


def register(request):
    if request.method == 'GET':
        return render(request, "register.html")

    elif request.method == 'POST':
        if request.POST["formType"] == 'login':
            userid = request.POST["loginusername"]
            user_pass = request.POST["loginuserpass"]

            
            auth_id = ''
            if not verifyEmail(userid):
                #not a email i.e. uk id.....
                auth_id = userid.upper()

            else:
                userid = RegisteredUsers.get_by_email(userid)
                #user entered email find uk_id related to it....
                if userid:
                    # auth_id = userid[0].uk_id # return error when no query set retuee
                    auth_id = userid[0].uk_id
                else:
                    return render(request, "register.html",{"err" :"Invalid email or password"}) #email/uk id does not exists

            # auth_id = uk_id
            webuser = authenticate(username=auth_id, password=user_pass) 
            if webuser is not None:
                # first check user has verified his email though otp at the time of registration.....if not then redirect to otp page... else login 
                # ru =  RegisteredUsers.get_by_id(auth_id)[0]#fniding user by uk_id
                login(request, webuser)
                return redirect("homepage")

                # if ru.active_status: # is otp verified...
                    #email is verifies through otp (yes verified)
                # else:#no top not verified send an new otp....
                #     #add email to session
                #     request.session["user"] = ru.email

                #     otp = random.randrange(1000, 9999)
                #     ru.OTP = otp
                #     ru.save()

                #     sendOTP(ru.email, ru.name, otp, ru.uk_id)
                #     #email is not verified yet using OTP... send otp again again and verify email first....
                #     return render(request, "otp.html", {"err":f"test otp: {otp}","msg":"You havent verified email on registration please verify email first"})
            else:
                return render(request, "register.html",{"err" :"Invalid email or password"})
        else:
            #register 
            name = request.POST['regusername']
            email = request.POST['regemail']
            phone = request.POST['regphone']
            college = request.POST['regcollege']
            course = request.POST['course']
            gender = request.POST['reggender']
            city = request.POST['regcity']
            password = request.POST['regpass']
            # ca_refferral = request.POST['carefferal']
            ukid = generateUtkarshId()

            #check if email exists or not.... if exists cancel registration...
            s = RegisteredUsers.get_by_email(email)
            ##check if ca refferal code exists....
            # ca_ref = CampusAmbassador.get_by_ambassador_id(ca_refferral)
            

            if s:
                #any user with this email found...( ask the chage email register again )
                return render(request, "register.html",{"foo" :"User With same email already exists.","name":name,"email":email, "course":course,"phone":phone,"college":college,"city":city})
            # elif ca_refferral != "" and not ca_ref:
            #     return render(request, "register.html",{"foo" :"Invalid CA Refferal Code","name":name,"email":email, "course":course,"phone":phone,"college":college,"city":city})
            else:
                # utf8mb4 for mysql
                auth_uer = DjangoUser.objects.create_user(username=ukid,email=email, first_name=name,password=password)
                auth_uer.save()

                webuser = RegisteredUsers(
                    uk_id = ukid,
                    name=name, 
                    email=email, 
                    phone=phone,
                    college_name=college,
                    course = course,
                    gender = gender,
                    city = city,
                    ca_refferal_code = "NA"
                    )
                webuser.save()

                # ca_ref[0].ca_attached_persons.add(webuser)

                request.session["user"] = email
                login(request, auth_uer)
                return redirect("homepage")
                # webuser = authenticate(username=auth_id, password=user_pass) 
                # sendOTP(email, name, otp, ukid)
                # return render(request, "otp.html", {"err":f"test otp: {otp}","msg":"This is trial OTP"})


def signout(request):
    print("logout")
    logout(request)
    return redirect("homepage")

# def verifyUser(request):
#     #verifies user email via otp....
#     mail = request.session.get("user")
#     u = RegisteredUsers.get_by_email(mail)[0]

#     if request.method == "POST":
#         otp = request.POST["otp"]
    
#         if(u.OTP == int(otp)):
#             #opt matched...
#             # print("sd", u.email)
#             u.active_status = True
#             u.save()
#             user = DjangoUser.objects.get(username=u.uk_id)
#             login(request, user)
#             return redirect('homepage')
#         else:
#             return render(request, "otp.html", {"err":"OTP mismatched","msg":"This is trial OTP"})
        
    # else:
    #     #GET method and resend OTP.....
    #     otp = random.randrange(1000, 9999)
    #     u.OTP = otp
    #     u.save()
    #     sendOTP(u.email, u.name, otp, u.uk_id)
    #     return render(request, "otp.html", {"err":f"OTP Resended {otp}","msg":"This is trial OTP "})


@csrf_exempt
def checkemail(request):
    m = ''
    s = RegisteredUsers.get_by_email(request.POST.get('email'))
    if s:m = "User with email already exists."
    else: m = "GoodToGo"
    return JsonResponse({"message":m})


@csrf_exempt
def unenroll_user(request):
    try:
        is_te = request.POST.get("isTE")
        uk_id = request.POST.get('username')
        ev_id = int(request.POST.get('event_id'))

        if is_te == "true":
            reg = TeamEventRegistrations.get_by_uk_id(uk_id)[0]
            reg.delete()
        
        else:
            user = RegisteredUsers.get_by_id(uk_id)[0]
            ev = SubSubEvents.get_by_id(ev_id)[0]
            user.enrolled_events.remove(ev)
        return JsonResponse({"msg":"Removed"})
    
    except Exception as e:
        print(e)
        return JsonResponse({"msg":"Failed"})


def EventsPage(request):
    if request.method == 'GET':
        category = request.GET.get('q')
        if not category:category = "all"

        ae =  UtkarshEvents.get_all_events()
        sub_events = SubEvents.get_all()

        if category == "all":
            sub_sub_event = SubSubEvents.get_all()
        else:
            sub_sub_event = SubSubEvents.get_by_parent_id(int(category))
            
        enrolled_events = ru = ambassador_data = tevr = accomodation_details = payments = ''
        if request.user.is_authenticated:
            ru = RegisteredUsers.get_by_id(request.user.username)[0]
            tevr = TeamEventRegistrations.get_by_uk_id(ru.uk_id)
            enrolled_events =  ru.enrolled_events.all()

            accomodation_details = Accomodation.get_by_person_id(ru)

            # enrolled_tevr = tevr.event_registered
            if ru.is_ambassador:
                ambassador_data = CampusAmbassador.get_ca_by_uk_id(ru.uk_id)[0]
                ambassador_data = ( ambassador_data.ca_attached_persons.all(), ambassador_data)


        return render(request, "events.html",{"payments":PAYMENT_DISCLAIMER,"events":ae,"ru":ru,"subevents":sub_events,"sub_sub_event":sub_sub_event,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"tevr":tevr,"accomodation_details":accomodation_details})
    
    else:
        if not request.user.is_authenticated:
            return redirect("regpage")
        else:
            if REGISTRATIONS_ON:
                event_id = request.POST['event_enroll']

                get_event_object = SubSubEvents.get_by_id(int(event_id))[0]
                #enroll..

                get_user_object = RegisteredUsers.get_by_id(request.user.username)[0]
                get_user_object.enrolled_events.add(get_event_object)
                    
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                #closed registrations.....
                return redirect("registrationclosed")


@csrf_exempt
def UK_id_verify(request):
    if request.method == 'POST':
        ru = RegisteredUsers.get_by_id(request.POST['entry'].upper())
        if ru:
            return JsonResponse({"msg":"ok", "name":ru[0].name})    
        else:
            return JsonResponse({"msg":"no"})



def TeamReg(request):
    if request.user.is_authenticated:

        ru = RegisteredUsers.get_by_id(request.user.username)[0]
        enrolled_events =  ru.enrolled_events.all()
        tevr = TeamEventRegistrations.get_by_uk_id(ru.uk_id)

        accomodation_details = Accomodation.get_by_person_id(ru)
        # enrolled_events = EventRegistraions.get_by_uk_id(request.user.username)
        ambassador_data = ''
        if ru.is_ambassador:
            ambassador_data = CampusAmbassador.get_ca_by_uk_id(ru.uk_id)[0]
            ambassador_data = ( ambassador_data.ca_attached_persons.all(), ambassador_data)
        
     
        if request.method == 'GET':
            ev = SubSubEvents.get_by_id(int(request.GET.get('eid')))
            return render(request,"teamEventRegistration.html", {"payments":PAYMENT_DISCLAIMER,"ru":ru,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"eid":ev[0],"tevr":tevr,"accomodation_details":accomodation_details})
        
        else:
            # POST
            ev =  SubSubEvents.get_by_id(int(request.GET.get('eid')))
            leader = request.user.username

            team_entries = request.POST["teammates"].upper()

            #check it there is no Team registration for this UKID
            tr = TeamEventRegistrations.get_by_uk_id(leader)
            if not tr:
                tm = []
                #verify all team member UK IDs..
                for team_m in team_entries.split(","):
                        ru = RegisteredUsers.get_by_id(team_m)
                        if ru:
                            tm.append(ru[0])
                        else:
                            return render(request,"teamEventRegistration.html",{"err":f"Invalid UK Id {team_m}","team_entries":team_entries, "ru":ru,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"eid":ev[0],"tevr":tevr})
                
                new_tr = TeamEventRegistrations(
                    team_leader_uk_id = leader,
                    event_registered = ev[0],
                    fee = ev[0].registration_amount
                )
                new_tr.save()
                new_tr.team_members.add(*tm)
                return redirect("eventsPage")
                
            else:
                return render(request,"teamEventRegistration.html",{"err":"You Can be leader of only one team","ru":ru,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"eid":ev[0],"tevr":tevr})
                
    else:
        return redirect("regpage")

@csrf_exempt
def AddAccomodation(request):
    if request.method == 'POST':
        #applying for accomodation.....
        user = RegisteredUsers.get_by_id(request.user.username)[0]

        acc = Accomodation.get_by_person_id(user)

        if request.POST["accomodationUpdate"] == "y":
            # add accomodation...
            if not acc:
                new_Ac = Accomodation(person = user)
                new_Ac.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            
            #remove from accomodation
            acc[0].delete()
            return redirect(request.META.get('HTTP_REFERER'))



from django.http import HttpResponse

def get_content_type(k):
    k = k.lower().split('.')[1]
    if k=="jpg" or k== "jpeg" or k== "png":
        return  (f"image/{k}")
    elif k == "pdf":
        return (f"application/pdf")
    elif k == 'mp4':
        return ("video/mp4")
    elif k == "gif":
        return ("image/gif")

def ShowStaticContents(request):
    try:
        l  = request.GET.get('n')
        with open( settings.MEDIA_ROOT / f'UtkarshWebsite/static/deliver/{l}', 'rb') as f:
            resp = HttpResponse(f.read(), content_type=get_content_type(l))
            return resp
    except:
        return HttpResponse("<h2>File not found..</h2>")


def RegistrationClose(request):
    if request.user.is_authenticated:
        ru = RegisteredUsers.get_by_id(request.user.username)[0]
        enrolled_events =  ru.enrolled_events.all()
        tevr = TeamEventRegistrations.get_by_uk_id(ru.uk_id)

        accomodation_details = Accomodation.get_by_person_id(ru)
        # enrolled_events = EventRegistraions.get_by_uk_id(request.user.username)
        ambassador_data = ''
        if ru.is_ambassador:
            ambassador_data = CampusAmbassador.get_ca_by_uk_id(ru.uk_id)[0]
            ambassador_data = ( ambassador_data.ca_attached_persons.all(), ambassador_data)
        
     
    return render(request,"closed.html", {"payments":PAYMENT_DISCLAIMER,"ru":ru,"enrolled_events":enrolled_events,"ambassador_data":ambassador_data,"tevr":tevr,"accomodation_details":accomodation_details})
        


def ResetPassword(request):
    if request.method == "POST":
        pass
    else:
        return render(request,"resetpass.html")