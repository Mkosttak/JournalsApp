from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Contact


def index(request):
    return render(request, "pages/index.html")


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.')
            return redirect('pages:contact')
    else:
        form = ContactForm()

    return render(request, "pages/contact.html", {'form': form})

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_contact(request):
    search_query = request.GET.get('q', '')
    messages = Contact.objects.all().order_by('is_answered', '-created_at')
    
    if search_query:
        messages = messages.filter(
            name__icontains=search_query) | messages.filter(
            email__icontains=search_query) | messages.filter(
            subject__icontains=search_query) | messages.filter(
            message__icontains=search_query)
    
    return render(request, 'pages/admin-contact.html', {
        'messages': messages
    })

@login_required
@user_passes_test(is_superuser)
def get_message(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    return JsonResponse({
        'name': message.name,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
        'created_at': message.created_at.isoformat()
    })

@login_required
@user_passes_test(is_superuser)
def reply_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Contact, id=message_id)
        subject = request.POST.get('subject')
        reply_message = request.POST.get('message')
        
        try:
            # E-posta gönderme
            send_mail(
                subject,
                reply_message,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],
                fail_silently=False,
            )
            
            # Mesajı yanıtlandı olarak işaretle
            message.is_answered = True
            message.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_superuser)
def delete_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Contact, id=message_id)
        try:
            message.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_superuser)
def toggle_message_status(request, message_id):
    if request.method == 'POST':
        try:
            message = get_object_or_404(Contact, id=message_id)
            # Mevcut durumun tersini al
            message.is_answered = not message.is_answered
            message.save()
            
            return JsonResponse({
                'success': True,
                'new_status': message.is_answered,
                'message': "Mesaj durumu başarıyla güncellendi"
            })
        except Contact.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Mesaj bulunamadı'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Geçersiz istek metodu'
    }, status=400)