from django.forms import ModelForm
from django import forms
from service.models import UserProfile, Category, Service,Review
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ("address", "phone_number", "birthday", "image")
        widgets = {
            "address": forms.Textarea(attrs={
                "placeholder": "Your address",
                "rows": 3,
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "Phone number",
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
            "birthday": forms.DateInput(attrs={
                "type": "date",
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
        }
    def clean_phone_number(self):
            phone = self.cleaned_data.get("phone_number")
            if phone:
                if not phone.isdigit():
                    raise forms.ValidationError("Phone number must contain only digits.")
                if len(phone) != 10:
                    raise forms.ValidationError("Phone number must be 10 digits.")
            return phone
    def clean_birthday(self):
            birthday = self.cleaned_data.get("birthday")
            if birthday and birthday > timezone.now().date():
                raise forms.ValidationError("Birthday cannot be in the future.")
            return birthday

class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.exclude(name__iexact="admin"),
        required=True,
        empty_label="Select Group",
        widget=forms.Select(attrs={
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 px-4 py-2"
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create password",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm password",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    first_name = forms.CharField(
        label="Enter your lastname",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter firstname",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    last_name = forms.CharField(
        label="Enter your firstname",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter lastname",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "group", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Enter username",
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
        }
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class ServiceForm(ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 px-4 py-2"
        })
    )

    class Meta:
        model = Service
        fields = ("title", "description", "price", "delivery_time", "categories")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
            "description": forms.Textarea(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
            "price": forms.TextInput(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
            "delivery_time": forms.TextInput(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
        }
    def clean_price(self):
            price = self.cleaned_data.get("price")
            if price is not None and price <= 0:
                raise forms.ValidationError("Price must be greater than zero.")
            return price

    def clean_delivery_time(self):
            delivery_time = self.cleaned_data.get("delivery_time")
            if delivery_time is not None and delivery_time <= 0:
                raise forms.ValidationError("Delivery time must be a positive number.")
            return delivery_time

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2",
                "placeholder": "Enter Category name"
            }),
            "description": forms.Textarea(attrs={
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2",
                "placeholder": "Enter Description"
            })
        }

class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    first_name = forms.CharField(
        label="Enter your lastname",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter firstname",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    last_name = forms.CharField(
        label="Enter your firstname",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter lastname",
            "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
        })
    )
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Enter username",
                "class": "block w-full rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800 placeholder-gray-400 px-4 py-2"
            }),
        }

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(attrs={
                "class": (
                    "block w-full rounded-lg border border-gray-300 bg-white "
                    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 "
                    "text-gray-800 placeholder-gray-400 px-4 py-2"
                )
            }),
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Share your thoughts about this service...",
                "class": (
                    "block w-full rounded-lg border border-gray-300 bg-white "
                    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 "
                    "text-gray-800 placeholder-gray-400 px-4 py-2"
                )
            }),
        }