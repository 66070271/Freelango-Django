from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,update_session_auth_hash
from django.contrib.auth.models import User
from .forms import UserProfileForm,CustomUserCreationForm,CategoryForm,ServiceForm,CustomUserChangeForm,ReviewForm
from .models import UserProfile,Category,ServiceImage,Service,Order,Payment,PlatformAccount,Review
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.decorators import permission_required,login_required
from django.http import HttpResponseForbidden

# Create your views here.
def loginView(request):
    if request.method == "POST":
        print("POST")
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request,'login.html', {"form":form})

def register(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            selected_group = user_form.cleaned_data["group"]
            user.groups.add(selected_group)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect("login")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, "register.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })
def home(request):
    query = request.GET.get('search', '')  # รับค่าจาก search bar
    if query:
        services = Service.objects.filter(title__icontains=query)
    else:
        services = Service.objects.all().order_by('-created_at')
    return render(request,"service.html",{"services":services})

def logoutView(request):
        logout(request)
        return redirect('login')




def service_detail(request,pk):
    service = Service.objects.get(pk=pk)
    reviews = Review.objects.filter(order__service=service).order_by('-created_at')
    return render(request,"service_detail.html",{"service":service,"reviews":reviews})
    
@permission_required("service.change_service", raise_exception=True)
def edit_service(request,pk):
    service =  Service.objects.get(pk=pk)
    if request.method == "POST":
        service_form = ServiceForm(request.POST,instance=service)
        if service_form.is_valid():
            service_form.save()
            return redirect("service_detail",pk=service.id)
        else:
            return render(request,'edit_service.html',{"form":service_form,"service":service})
    service_form = ServiceForm(instance=service)
    print(service.categories.all())
    return render(request,'edit_service.html',{"form":service_form,"service":service})

@permission_required("service.delete_service", raise_exception=True)    
def delete_service(request,pk):
    service = Service.objects.get(pk=pk)
    service.delete()
    return redirect('home')

@permission_required("service.add_service", raise_exception=True)
def add_service(request):
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        print(service_form.is_valid())
        if service_form.is_valid():
            service = service_form.save(commit=False)
            service.freelancer = request.user
            service.save()
            category = service_form.cleaned_data['categories']
            service.categories.set(category)
            for img in request.FILES.getlist('image'):
                ServiceImage.objects.create(service = service, image= img)
            return redirect('home')
        else:
            return render(request,'add_service.html',{"form":service_form})
    service_form = ServiceForm()
    return render(request,"add_service.html",{"form":service_form})

@permission_required("service.add_category", raise_exception=True)
def add_category(request):
    if request.method == "POST":
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('category_list')
    category_form = CategoryForm()
    return render(request,"add_category.html",{"form":category_form})

@permission_required("service.view_category", raise_exception=True)
def category_list(request):
    categories = Category.objects.all()
    return render(request,"category_list.html",{"categories":categories})

@permission_required("service.change_category", raise_exception=True)
def edit_category(request,pk):
    category = Category.objects.get(pk=pk)
    if request.method == "POST":
        category_form = CategoryForm(request.POST,instance=category)
        category_form.save()
        return redirect('category_list')
    category_form = CategoryForm(instance=category)
    return render(request,'edit_category.html',{"form":category_form,"category":category})

@permission_required("service.delete_category", raise_exception=True)
def delete_category(request,pk):
    category = Category.objects.get(pk=pk)
    category.delete()
    return redirect('category_list')


@permission_required("service.view_userprofile")
def profileView(request,pk):
    user = User.objects.get(pk=pk)
    profile = UserProfile.objects.get(user = user)
    return render(request,"profile.html",{"profile":profile})

@permission_required("service.change_userprofile")
def edit_profile(request,pk):
    user = User.objects.get(pk=pk)
    profile = UserProfile.objects.get(user = user)
    if request.method == "POST":
        print(request.FILES)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=profile)
        user_form = CustomUserChangeForm(request.POST,instance=request.user)
        print(profile_form.is_valid(),user_form.is_valid())
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return redirect("profile_view", pk=user.id)
        else:
            return render(request, "edit_profile.html", {
                "profile_form": profile_form,
                "user_form": user_form,
                "profile": profile,
            })

    profile_form = UserProfileForm(instance=profile)
    user_form = CustomUserChangeForm(instance=request.user)
    return render(request,"edit_profile.html",{"profile_form":profile_form,"user_form":user_form,"profile":profile})

@permission_required("service.add_order")
def checkout_view(request,pk):
    bank = PlatformAccount.objects.first()
    service = Service.objects.get(pk=pk)
    if request.method == "POST":
        order = Order.objects.create(service = service,client = request.user,price = service.price)
        payment = Payment.objects.create(order = order,method = request.POST['payment_method'])
        return redirect("confirm_payment",pk=order.id)  
    return render(request,"checkout.html",{"service":service,"bank":bank})

@permission_required("service.add_payment")
def confirm_payment(request,pk):
    order = Order.objects.get(pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "upload_now":
            slip = request.FILES.get("slip")
            if slip:
                payment = Payment.objects.get(order=order)
                payment.transaction_ref = slip  # หรือใช้ฟิลด์ 
                payment.status = "paid"
                payment.save()
                return redirect("home")
            else:
                redirect('confirm_payment')
        elif action == "upload_later":
            return redirect("order_list")
    return render(request,"confirm_payment.html",{"order":order})

@permission_required("service.add_order", raise_exception=True)
def confirm_work(request,pk):
    order = Order.objects.get(pk=pk)
    order.status = "confirmed"
    order.save()
    return redirect('order_list')

@permission_required("service.view_order")
def order_list(request):
    orders = Order.objects.filter(client = request.user).order_by('-updated_at')
    return render(request,"order_list.html",{"orders":orders})

@permission_required("service.view_order")
def order_detail(request,pk):
    bank = PlatformAccount.objects.first()
    order = Order.objects.get(pk=pk)
    payment = Payment.objects.get(order = order)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "cancel_order":
            if order.payment.status != "pending":
                order.status = "cancelled"
                order.save()
                print(1)
                return redirect('order_list')
            else:
                order.status = "cancelled"
                order.payment.status = "cancelled"
                order.save()
                order.payment.save()
                print(order.payment)
                print(order.payment.status)
                return redirect('order_list')
    return render(request,'order_detail.html',{"order" : order,"payment":payment,"bank":bank})

@permission_required("service.approve_payment", raise_exception=True)
def admin_order(request):
    orders = Order.objects.filter(Q(status ="cancelled",payment__status = "confirmed") | Q(status ="pending",payment__status = "paid") | Q(status = "cancelled",payment__status = "paid") | Q(status = "confirmed",payment__status = "confirmed")).order_by('-updated_at')
    return render(request,"admin_order.html",{"orders":orders})

@permission_required("service.approve_payment", raise_exception=True)
def approve_payment(request,pk):
    order = Order.objects.get(pk=pk)
    payment = Payment.objects.get(order=order)
    payment.status = "confirmed"
    payment.save()
    return redirect('admin_order')

@permission_required("service.approve_refund", raise_exception=True)
def approve_refund(request,pk):
    order = Order.objects.get(pk=pk)
    payment = Payment.objects.get(order=order)
    payment.status = "refunded"
    payment.save()
    return redirect('admin_order')

@permission_required("service.manage_order", raise_exception=True)
def work_list(request):
    order = Order.objects.filter(service__freelancer = request.user).order_by('-updated_at')
    return render(request,"work_list.html",{"orders":order})

@permission_required("service.manage_order", raise_exception=True)
def work_action(request,pk):
    order = Order.objects.get(pk=pk)
    print(order)
    client = order.client
    profile = UserProfile.objects.get(user = client)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept":
            print("accept")
            order.status = "in_progress"
            order.save()
            return redirect('work_list')
        elif action == "cancel":
            order.status = "cancelled"
            order.save()
            return redirect('work_list')
        elif action == "send":
            return render(request,'profile.html',{"profile" : profile})
        elif action == "finish":
            order.status = "completed"
            order.save()
            return redirect('work_list')
@permission_required('service.add_review')       
def add_review(request, pk):
    order = Order.objects.get(pk=pk)
    service = order.service
    freelancer = order.service.freelancer
    if not order.client.id == request.user.id:
        return HttpResponseForbidden("You are not allowed to review this service.")
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            review.freelancer = freelancer
            review.service = service
            review.order = order
            review.save()
            return redirect("service_detail", pk=service.id)
    else:
        form = ReviewForm()
    return render(request, "add_review.html", {"form": form, "service": service})

@permission_required('service.delete_review')
def delete_review(request, pk):
    review = Review.objects.get(pk=pk)
    if request.user != review.client and not request.user.is_staff:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบรีวิวนี้")
    review.delete()
    return redirect('service_detail', pk=review.order.service.id)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('home')  
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})
@permission_required("auth.change_user")
def user_list(request):
    query = request.GET.get("q", "")
    users = User.objects.all()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(groups__name__icontains=query)
        ).distinct()
    return render(request, "user_list.html", {"users": users})
@permission_required("auth.delete_user", raise_exception=True)
def delete_user(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return redirect("user_list")
