#from ast import Or
from email import message
import imp
import re
#from tokenize import group
from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.mail import send_mail
import random

# Create your views here.
def Home(request):
    return render(request,'carousel.html')

def About(request):
    return render(request,'about.html')

def Contact(request):
    return render(request,'contact.html')

#hii
def Gallery(request):
    return render(request,'gallery.html')

def Login_User(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        print("fiiii "+p)
        user = authenticate(username=u, password=p)
        print(user)
        sign = ""
        if user and not user.is_staff:
            login(request, user)
            messages.success(request, "Logged in Successfully")
            return redirect('home')
        else:
            messages.success(request, "Invalid user")
    return render(request, 'login.html')

def admin_login(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if user and  user.is_staff:
            login(request, user)
            messages.success(request, "Logged in Successfully")
            return redirect('admin_home')
        else:
            messages.success(request, "Invalid user")
    return render(request, 'admin_login.html')

def Signup_User(request):
    cat = Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        d = request.POST['dob']
        con = request.POST['contact']
        add = request.POST['add']
        group = request.POST['group']
        im = request.FILES['image']
        cat = Category.objects.get(id=group)
        user=None
        try:
         user = User.objects.get(username=u)
         messages.error(request, "username already exist")
         return redirect('signup')
        except:        
         user=None 
        user = User.objects.create_user(email=e, username=u, password=p, first_name=f,last_name=l)
        UserProfile.objects.create(user=user,contact=con,address=add,image=im,dob=d, blood_group=cat)
        mm='Hello '+f+l+'<br><br>Your Personal Details(Don\'t share to anyone)<br><br>Username: '+u+'<br>Password: '+p+'<br><br>Welcome to our Aspire Blood Bank'
        send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[e],html_message=mm)
        messages.success(request, "Registration Successful")
        cat = Category.objects.filter(id=group)
        return redirect('home')
    return render(request,'register.html', {'cat':cat})

def Logout(request):
    logout(request)
    return redirect('home')

def Change_Password(request):
    user = User.objects.get(username=request.user.username)
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            m='hi '+u.username+'<br><br>Your Password is successfully changed'
            send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[u.email],html_message=mm)
            messages.success(request, "Password changed successfully")
        else:
            messages.success(request, "New password and confirm password are not same.")
        return redirect('home')
    return render(request,'change_password.html')


def view_user(request):
    data = UserProfile.objects.all()
    d = {'data':data}
    return render(request,'view_user.html',d)

def edit_profile(request,pid):
    data = UserProfile.objects.get(id=pid)
    cat = Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        cat = request.POST['group']
        try:
            im = request.FILES['image']
            data.image=im
            data.save()
        except:
            pass
        data.user.first_name = f
        data.user.last_name = l
        data.user.email = e
        data.contact = con
        bl = Category.objects.get(id=cat)
        data.blood_group = bl
        data.address = add
        data.user.save()
        data.save()
        messages.success(request, "User Profile updated")
        if request.user.is_staff:
            return redirect('view_user')
        else:
            return redirect('profile')
    d = {'data':data, 'cat':cat}
    return render(request,'edit_profile.html',d)

def profile(request):
    pro = UserProfile.objects.get(user=request.user)
    return render(request, "profile.html", {'pro':pro})

def add_category(request):
    if request.method == 'POST':
        n = request.POST['name']
        Category.objects.create(name=n)
        messages.success(request, "Category created successfully")
        return redirect('view_category')
    return render(request, 'add_category.html')

def edit_category(request, pid):
    data = Category.objects.get(id=pid)
    if request.method == 'POST':
        n = request.POST['name']
        data.name=n
        data.save()
        messages.success(request, "Category Updated successfully")
        return redirect('view_category')
    return render(request, 'edit_category.html',{'data':data})

def view_category(request):
    data = Category.objects.all()
    return render(request, 'view_category.html', {'data':data})

def delete_category(request, pid):
    data = Category.objects.get(id=pid)
    data.delete()
    messages.success(request, "Category deleted successfully")
    return redirect('view_category')

def search_blood(request):
    userprofile = UserProfile.objects.get(user=request.user)
    data = Blood_Donation.objects.filter(status="Approved").exclude(purpose="Request for Blood", user=userprofile)
    if request.method == "POST":
        bg = request.POST['group']
        place = request.POST['place']
        cat = Category.objects.get(id=bg)
        user = UserProfile.objects.get(user=request.user)
        Blood_Donation.objects.create(blood_group=cat, user=user, purpose="Request for Blood", status="Pending", place=place)
        messages.success(request, "Request Generated.")
        return redirect('search_blood')
    all_cat = Category.objects.all()
    return render(request, 'search_blood.html', {'data':data, 'cat':all_cat})

def donate_blood(request):
    if request.method == "POST":
        bg = request.POST['group']
        place = request.POST['place']
        cat = Category.objects.get(id=bg)
        user = UserProfile.objects.get(user=request.user)
        data = Blood_Donation.objects.create(blood_group=cat, user=user, purpose="Blood Donor", status="Pending", place=place)
        m='Hi '+request.user.first_name+' '+request.user.last_name+'<br><br>Thanks for donate your blood'
        send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[request.user.email],html_message=m)
        messages.success(request, "Added Your Detail.")
        return redirect('donate_blood')

    all_cat = Category.objects.all()
    return render(request, 'donate_blood.html', {'cat':all_cat})

def request_blood(request):
    mydata = request.GET.get('action',0)
    data = Blood_Donation.objects.filter(purpose="Request for Blood")
    if mydata:
        data = data.filter(status=mydata)
    return render(request, 'request_blood.html', {'data':data})

def donator_blood(request):
    mydata = request.GET.get('action',0)
    data = Blood_Donation.objects.filter(purpose="Blood Donor")
    if mydata:
        data = data.filter(status=mydata)
    return render(request, 'donator_blood.html', {'data':data})

def change_status(request,pid):
    data = Blood_Donation.objects.get(id=pid)
    url = request.GET.get('data')
    if data.status == "Approved":
        data.status = "Pending"
        data.save()
    else:
        user=data.user.user
        print(type(user))
        print(user.username)
        data.status = "Approved"
        m='hi '+user.first_name+' '+user.last_name+'<br><br>Your pending request for blood donate is approved'
        send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[user.email],html_message=m)
        data.save()
    return HttpResponseRedirect(url)

def admin_home(request):
    data = UserProfile.objects.all()
    order = Order.objects.all()
    donate = Blood_Donation.objects.filter(purpose="Blood Donor")
    req = Blood_Donation.objects.filter(purpose="Request for Blood")

    d = {'data':data.count(), 'order':order.count(), 'req':req.count(), 'donate':donate.count()}
    return render(request,'admin_home.html',d)

def history(request):
    user = UserProfile.objects.get(user=request.user)
    data = Blood_Donation.objects.filter(user=user)
    return render(request, "history.html", {'data':data})

def pay_now(request, pid):
    total = 2000
    user = UserProfile.objects.get(user=request.user)
    blood = Blood_Donation.objects.get(id=pid)
    if request.method == "POST":
        Order.objects.create(user=user, blood_donation=blood, amount=total, status="Pending")
        m='hi '+request.user.first_name+' '+request.user.first_name+'<br><br>Your order details'
        send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[request.user.email],html_message=m)
        messages.success(request, "Ordered Succesfully")
        return redirect("my_order")
    if request.GET.get('get') == "1":
        Order.objects.create(user=user, blood_donation=blood, amount=total, status="Pending")
        messages.success(request, "Ordered Succesfully")
        m='hi '+request.user.first_name+' '+request.user.first_name+'<br><br>Your order details'
        send_mail('Aspire Blood Bank','',settings.EMAIL_HOST_USER,[request.user.email],html_message=m)
        return redirect("my_order")
    return render(request, "payment2.html",{'total':total})

def my_order(request):
    user = UserProfile.objects.get(user=request.user)
    data = Order.objects.filter(user=user)
    return render(request, "my_order.html",{'data':data})

def all_order(request):
    data = Order.objects.filter()
    return render(request, "all_order.html",{'data':data})

def delete_order(request, pid):
    data = Order.objects.get(id=pid)
    data.delete()
    messages.success(request, "Order deleted successfully")
    return redirect('my_order')

def delete_user(request, pid):
    data = UserProfile.objects.get(id=pid)
    data.delete()
    messages.success(request, "User deleted successfully")
    return redirect('view_user')


def change_order_status(request,pid):
    data = Order.objects.get(id=pid)
    if data.status == "Delivered":
        data.status = "Pending"
        data.save()
    else:
        data.status = "Delivered"
        data.save()
    messages.success(request, "Order Status changed successfully")
    return redirect('all_order')
