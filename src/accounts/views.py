from allauth.account.models import EmailAddress
from django.shortcuts import render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions, status
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from src.accounts.models import User
from src.accounts.serializers import CustomRegisterAccountSerializer
from src.accounts.tokens import account_activation_token


# class LoginView(View):
#     def post(self, request):
#         form = AuthenticationForm(request=request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             if user.is_superuser or user.is_staff:
#                 login(request, user)
#                 if 'next' in request.POST:
#                     return HttpResponseRedirect(reverse('next'))
#                 else:
#                     return HttpResponseRedirect(reverse('administration:dashboard'))
#             else:
#                 messages.error(
#                     request, "You are not allowed to access administration. Need help? Please consult admin"
#                 )
#         return render(request, 'accounts/login.html', {'form': form})

#     def get(self, request):
#         if request.user.is_authenticated:
#             if request.user.is_superuser or request.user.is_staff:
#                 return redirect('administration:dashboard')
#             else:
#                 logout(request)
#                 messages.error(
#                     request, "You are not allowed to access administration. Need help? Please consult admin"
#                 )
#                 return redirect('accounts:administration-login')

#         form = AuthenticationForm()
#         return render(request=request, template_name='accounts/login.html', context={'form': form})


# @method_decorator(login_required, name='dispatch')
# class LogoutView(View):
#
#     def get(self, request):
#         logout(request)
#         return redirect('accounts:administration-login')


# class GoogleLoginView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client
#     callback_url = GOOGLE_CALLBACK_ADDRESS


# class FacebookLoginView(SocialLoginView):
#     adapter_class = FacebookOAuth2Adapter


class CustomRegisterAccountView(APIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = {}
        status_code = status.HTTP_400_BAD_REQUEST
        serializer = CustomRegisterAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            data = {'success': 'Account created successfully'}
            status_code = status.HTTP_201_CREATED

            current_site = get_current_site(request)
            mail_subject = 'Activate your TaskTok account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()

        else:
            data = serializer.errors
        return Response(data=data, status=status_code)


def view_activate(request, uidb64, token):
    try:

        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        try:
            email_account = EmailAddress.objects.get(user=user)
        except EmailAddress.DoesNotExist:
            email_account = EmailAddress.objects.create(
                user=user, email=user.email, primary=True
            )
        email_account.verified = True
        email_account.save()

        user.save()
        # return redirect('home')
        return render(
            request,
            template_name='accounts/signup_confirm.html',
            context={
                'message': 'Thank you for your email confirmation, GOOD LUCK! help the needy, make your '
                           'profile, be a reason of someone to smile and become a HERO.'
            }
        )
    else:
        return render(
            request,
            template_name='accounts/signup_confirm.html',
            context={'message': 'unable to activate account because the activation link is invalid'}
        )
