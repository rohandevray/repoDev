from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from scheduling.models import Organization,User,Membershiplevel,Teamrequest, Event
from userauth.models import Account
from gsetup import service, google_create_event, google_update_event  
import datetime
from .utils import is_time_between
# Create your views here.
import pytz

utc=pytz.UTC

# function used for retrieving ids of child organisations
def retrieve_child_org(parent,child):
    count = Organization.objects.filter(parent_org = parent).count()
    if count!=0:
        child_org = Organization.objects.filter(parent_org = parent)
        for i in child_org:
            retrieve_child_org(i.id,child)
            child.append(i.id)

###################################################################################################################################################

def create_team(request,par_id) :

    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['team_name']
            members = request.POST.getlist('checks')
            print(members)
            user=request.user
            description = request.POST['description']
            if Organization.objects.filter(name = team_name,parent_org__id = par_id).exists():
                warning = "team with that name already exists"
            elif Membershiplevel.objects.get(user_id = request.user.id,organization_id = par_id).role == 1 : #If user is an admin
                org = Organization.objects.create(name = team_name,parent_org_id = par_id,description = description)
                members = User.objects.filter(pk__in = members)
                #Membershiplevel.create_team(members,org,par_id)
                Membershiplevel.create_team(members,org,par_id,request.user.id)
                warning = "team created"
            else :
                Teamrequest.create_team_req(user,team_name,description,par_id,members) #If user is a participant
                warning = "team request sent to admin"
        memberships = Membershiplevel.objects.filter(organization__id = par_id)
        return render(request,'create_team.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')

def create_new_team(request):

    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['team_name']
            members = request.POST.getlist('checks')
            user=request.user
            description = request.POST['description']
            print(members)
            if Organization.objects.filter(name = team_name,parent_org__id = None).exists():
                warning = "team with that name already exists"
            else:
                org = Organization.objects.create(name = team_name,parent_org_id = None)
                members = User.objects.filter(pk__in = members)
                Membershiplevel.create_team(members,org,None,request.user.id)
                warning = "team created"
        memberships = Account.objects.all()
        return render(request,'create_team.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')


def team_request(request, par_id) :
    if request.user.is_authenticated:
        user = request.user
        top_org = Organization.get_top_org(par_id)
        print("top_org:",top_org)
        all_sub_org = Organization.get_all_children(top_org)
        print("sub orgs:",all_sub_org)
        sub_org = Membershiplevel.get_subgroups(all_sub_org, user)
        print("sunGroups:",sub_org)
        tr_request = Teamrequest.objects.filter(par_org__in = sub_org, status = 2) 
        print("team request:",tr_request)
        print(tr_request) 
        return render(request,'team_request.html',{'team_request':tr_request,'user':request.user })
    else:
        return redirect('/userauth/login')

def change_role(request,org_id):
    if request.user.is_authenticated:
        warning = ''
        role = Membershiplevel.objects.get(organization__id = org_id , user_id = request.user.id).role
        if request.method == 'POST':
            print("inside the change_role fun")
            members = request.POST.getlist('checks')
            print(members)
            members = User.objects.filter(pk__in = members)
            Membershiplevel.change_role(members,org_id)
            warning = "role changed to admin"
        memberships = Membershiplevel.objects.filter(organization__id = org_id, role = 2)
        return render(request,'change_role_toadmin.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')

def dismiss_admin(request,org_id):
    if request.user.is_authenticated:
        warning = ''
        admin = Membershiplevel.objects.filter(organization__id = org_id,role = 1).count()
        if request.method == 'POST':
            print("inside")
            members = request.POST.getlist('checks')
            count = 0
            for member in members:
                count+=1
            print(members)
            if count==admin :
                warning = "can't turn into participant"
            else:
                members = User.objects.filter(pk__in = members)
                Membershiplevel.change_role_participant(members,org_id)
                warning = "role changed to participant"

        memberships = Membershiplevel.objects.filter(organization__id = org_id, role = 1)
        return render(request,'participant.html',{'memberships':memberships,'warning':warning,'user':request.user},)
    else:
        return redirect('/userauth/login')

def leave_team(request,org_id):
    if request.user.is_authenticated:
        warning=''     
        flag = False
        par_id = Organization.objects.get(pk=org_id).parent_org_id
        name = Organization.objects.get(pk=org_id).name
        while par_id is not None:
            role = Membershiplevel.objects.get(user_id = request.user.id, organization__id = par_id).role
            if role == 1:
                flag = True
                break
            par_id = Organization.objects.get(pk=par_id).parent_org
        if flag == True:
            warning = "Can't leave the team"
        else:
            # retrievig child organisations and storing their ids in child[]
            child = []
            retrieve_child_org(org_id,child)
            child.append(org_id)

            for org in child:
                # checking whether the user is a part of the organization
                if Membershiplevel.objects.filter(organization__id=org,user_id=request.user.id).exists():

                    role = Membershiplevel.objects.get(organization__id = org , user_id = request.user.id).role
                    p = User.objects.get(pk = request.user.id)
                    total_members = Membershiplevel.objects.filter(organization__id = org).count()
                    if total_members>1:
                        # if the person is admin
                        if role == 1:
                            admin = Membershiplevel.objects.filter(organization__id = org,role = 1).count()
                            # if count of admin >1 then he will easily leave the team
                            if admin>1:
                                Membershiplevel.leave_team(p,org)
                                warning = "Left the team"
                            else:  # if count of admin is one then before leaving some random person should be made as admin
                                members = Membershiplevel.objects.filter(organization__id = org)
                                # accessing the member of team which was first added to team. 
                                user = Membershiplevel.random_fun(members,org,request.user.id)
                                q = User.objects.filter(pk=user)
                                # making random person admin
                                Membershiplevel.change_role(q,org)
                                # admin leaving the team
                                Membershiplevel.leave_team(p,org)
                                warning = "Left the team"
                        else:
                            # if the person is participant
                            Membershiplevel.leave_team(p,org)
                            warning = "Left the team"
                    else: 
                        Membershiplevel.leave_team(p,org)
                        Organization.delete_org(org)
                        warning = "Left the team"
        return render(request,'leave_team.html',{'warning':warning,'user':request.user,'name':name},)
    else:
        return redirect('userauth/login')

#########################################################################################################
def remove_team(memberId,org_id):     
    flag = False
    par_id = Organization.objects.get(pk=org_id).parent_org_id
    while par_id is not None:
        role = Membershiplevel.objects.get(user_id = memberId, organization__id = par_id).role
        if role == 1:
            flag = True
            break
        par_id = Organization.objects.get(pk=par_id).parent_org
    if flag == False:
        # retrievig child organisations and storing their ids in child[]
        child = []
        retrieve_child_org(org_id,child)
        child.append(org_id)

        for org in child:
            # checking whether the user is a part of the organization
            if Membershiplevel.objects.filter(organization__id=org,user_id=memberId).exists():

                role = Membershiplevel.objects.get(organization__id = org , user_id = memberId).role
                p = User.objects.get(pk = memberId)
                total_members = Membershiplevel.objects.filter(organization__id = org).count()
                if total_members>1:
                    # if the person is admin
                    if role == 1:
                        admin = Membershiplevel.objects.filter(organization__id = org,role = 1).count()
                        # if count of admin >1 then he will easily leave the team
                        if admin>1:
                            Membershiplevel.leave_team(p,org)
                        else:  # if count of admin is one then before leaving some random person should be made as admin
                            members = Membershiplevel.objects.filter(organization__id = org)
                            # accessing the member of team which was first added to team. 
                            user = Membershiplevel.random_fun(members,org,memberId)
                            q = User.objects.filter(pk=user)
                            # making random person admin
                            Membershiplevel.change_role(q,org)
                            # admin leaving the team
                            Membershiplevel.leave_team(p,org)
                    else:
                        # if the person is participant
                        Membershiplevel.leave_team(p,org)
                else: 
                    Membershiplevel.leave_team(p,org)
                    Organization.delete_org(org)
#######################################################################################################################


def edit_team(request, org_id) :

    if request.user.is_authenticated:
        warning = ''
       
        if request.method == 'POST':
            team_name = request.POST['team_name']
            description = request.POST['description']
            new_members = request.POST.getlist('checks')

            old_team_name = Organization.objects.get(pk=org_id).name
            par_id = Organization.objects.get(pk = org_id).parent_org_id
            Organization.update_team(old_team_name,team_name,description,par_id)
            ex_members = Membershiplevel.objects.filter(organization__id = org_id)
            ids = []
            for i in ex_members:
                ids.append(i.user_id)
            ex_members = User.objects.filter(pk__in = ids)
            new_members = User.objects.filter(pk__in = new_members)
            for member in ex_members:
                if member not in new_members:
                    remove_team(member.id,org_id)
            
            user = request.user
            org  = Organization.objects.get(pk = org_id)
            
            Membershiplevel.edit_team(ex_members,new_members,org_id,par_id,request.user.id)
            warning = "successfully edited"
        par_id = Organization.objects.get(pk = org_id).parent_org_id
        if par_id is None:
            memberships = Account.objects.all()
        else:
            memberships = Membershiplevel.objects.filter(organization__id=par_id)
        organisation  = Organization.objects.get(pk = org_id)    
        return render(request, 'edit_team.html',{'memberships': memberships,'org': organisation, 'warning':warning, 'user': request.user},)
    else:
        return redirect('/userauth/login')


def ajax_change_status(request):
    if request.user.is_authenticated:
        request_status = request.GET.get('request_status', 2)
        print("request_status:",request_status)
        request_id = request.GET.get('request_id', False)
        print("request_id:",request_id)
        team_request = Teamrequest.objects.get(pk=request_id)
        print("team_request:",team_request)
        print("requestStatus:",team_request.status)
        print("Name:",team_request.team_name)
        print("Sender:",team_request.sender.id)
        print("description:",team_request.team_description)
        print("par_org:",team_request.par_org)
        print("members:",team_request.team_members.all())
        try:
            request_status = int(request_status)
            if team_request.status == 1 :
                return JsonResponse({"success": True,"status":"already approved"})
            elif team_request.status == 0 :
                return JsonResponse({"success": True,"status":"already rejected"})
            elif request_status == 1:
                print("entered")
                org = Organization.objects.create(name = team_request.team_name,parent_org_id = team_request.par_org.id)
                print("org:",org)
                Membershiplevel.create_team(team_request.team_members.all(),org,team_request.par_org,team_request.sender.id)
                team_request.status=1
                team_request.save()
                return JsonResponse({"success": True,"status":"approved"})
            elif request_status == 0:
                team_request.status = 0
                team_request.save()
                return JsonResponse({"success": True,"status":"rejected"}) 
        except Exception as e:
            print("Exceptiion:",Exception)
            return JsonResponse({"success": False})
    else:
        return redirect('/userauth/login')



def show_team(request, team_id):
    if request.user.is_authenticated:
        user = request.user
        org  = Organization.objects.get(pk = team_id)
        if not org:
            return  redirect('/userauth/home')
        children = Organization.get_all_children(org)
        members = Membershiplevel.objects.filter(organization__id = org.id)
        print(org.event.all())
        return render(request, 'show_team.html',{"org": org, "children": children, "members": members,'user':request.user})
    else:
        return redirect('/userauth/login')

def add_event(request, org_id):
    if request.user.is_authenticated:
        user = request.user
        org  = Organization.objects.get(pk = org_id)
        if not org:
            return redirect('/userprofile/create_team/1')
        if request.method == 'POST':
            start_date = request.POST['start-date']
            start_time = request.POST['start-time']
            end_date = request.POST['end-date']
            end_time = request.POST['end-time']
            start = str(start_date) +" "+str(start_time) + '+0000'
            end = str(end_date) +" "+str(end_time)+ '+0000'
            title = request.POST['title']
            start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M%z")
            end= datetime.datetime.strptime(end, "%Y-%m-%d %H:%M%z")
            if start>=end:
                return render(request,"add_event.html",{"warning": "Invalid time and/or inputs", "org":org,'user':request.user})
            description = request.POST['description']
            location = request.POST['location']
            all_events = Event.objects.all()
            clash_events = []
            for e in all_events:
                if is_time_between(start,end, e.start_time) or is_time_between(start,end, e.end_time) or is_time_between(e.start_time,e.end_time, end) or is_time_between(e.start_time,e.end_time, start):
                    clash_events.append(e)

            members = Membershiplevel.objects.filter(organization = org).values('user')
    
            for c in clash_events:
                org2  = c.organization
                mem2 = Membershiplevel.objects.filter(organization = org2).values('user')
                for m in mem2:
                    if m in members:
                        return render(request,'add_event.html',{"warning": "Clashes!!!!","org":org})
            attendees = []
           
            for m in members:
                print(m)
                user = User.objects.get(pk = m['user'])
                attendees.append({"email": user.email})
            event = google_create_event(location, title, description, start,end,"tentative", attendees)
            if event['id']:
                new_event = Event.objects.create(organization = org, title= title, description= description, location = location, start_time = start, end_time = end, status = 0, eventId = event['id'] )
                new_event.save()
                return render(request,"add_event.html",{"warning": "Success! Event Created", "org":org,'user':request.user})
            else:
                return render(request,"add_event.html",{"warning": "Failure! Couldn't create event, please try again","org":org,'user':request.user })
        else:
            return render(request, 'add_event.html', {"org": org,'user':request.user})
    else:
        return redirect('/userauth/login')

def view_event(request, event_id):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')

    print(event_id)
    event = Event.objects.get(pk=event_id)
    if not event:   
        return redirect('userprofile/view_team/1')
    members = Membershiplevel.objects.filter(organization = event.organization.id).values('user')
    attendees = User.objects.filter(pk__in = members)
    return render(request,'show_event.html', {'event': event , 'attendees': attendees,'user':request.user})

def update_event(request,event_id):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')

    event = Event.objects.get(pk = event_id)
    if not event:
        return redirect('userprofile/view_team/1')
    if request.method == 'POST':
        title = request.POST['title']
        location = request.POST['location']
        description = request.POST['description']
        start_date = request.POST['start-date']
        start_time = request.POST['start-time']
        end_date = request.POST['end-date']
        end_time = request.POST['end-time']
        start = str(start_date) +" "+str(start_time)
        end = str(end_date) +" "+str(end_time)
        # print(len(start))
        # print(len(end))
        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M")
        status  = request.POST['status']
        if status==0:
            status = "tentative"
        elif status==1:
            status = "cancelled"
        else:
            status = "confirmed"
        updated_event  = google_update_event(event.eventId, title, description, location, start, end, status)
        # print(updated_event)
        if not updated_event.get('id'):
            return render(request, 'update_event.html', {"event": event,'user':request.user,'warning':"Couldn't update event"})

        event.eventId = updated_event['id']
        event.title = updated_event['summary']
        event.location = updated_event['location']
        event.description = updated_event['description']
        if status == "tentative":
            event.status=0
        elif status == "cancelled":
            event.status=1
        else:
            event.status=2
       
        
        event.start_time = start
             
        event.end_time =  end
        print("event.start_time")
        print(event.start_time)
        print("event.end_time")
        print(event.end_time)
        print(event)
        event.save()
        return redirect('/userprofile/view_event/'+str(event.id))
    return render(request, 'update_event.html', {"event": event,'user':request.user,"warning": 'Event pdated Successfully'})

def view_calendar(request):
    if not request.user.is_authenticated:
        return redirect('/userauth/login')
    return render(request,'calendar.html',{'user':request.user})