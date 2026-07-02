import django
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import TenantForm
from a_tenant_manager.models import *
from django.core.management import call_command
from django.conf import settings
from django_tenants.utils import schema_context
from django.contrib.auth import login

def home_view(request):
    tenant_form = TenantForm()
    
    if request.method == 'POST':
        tenant_form = TenantForm(request.POST)
        if tenant_form.is_valid():
            tenant = tenant_form.save()
            call_command('migrate_schemas', schema_name=tenant.schema_name)
            
            domain = Domain.objects.create(
                tenant=tenant, 
                domain=f'{tenant.schema_name}.{settings.BASE_URL}', 
                is_primary=True
            ) 
            
            with schema_context(tenant.schema_name):
                request.user.backend = 'allauth.account.auth_backends.AuthenticationBackend' 
                login(request, request.user)  
                
            return redirect(f'http://{domain.domain}:{settings.PORT}/')  # Redirect to the new tenant's domain   
    
    context = {
        'tenant_form': tenant_form
    }
    return render(request, 'home.html', context)


# def create_item(request):
#     if request.POST: 
#         name = request.POST.get('name')
#         item = Item(name=name)
#         item.save()
#         return HttpResponse(f'<li class="text-8xl font-thin">{item.name}</li>')

#     else:
#         return redirect('home')