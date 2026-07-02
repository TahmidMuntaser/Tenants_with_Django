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
            
            TenantMember.objects.create(
                user = request.user,
                tenant = tenant, 
                is_admin = True
            )
            
            with schema_context(tenant.schema_name):
                request.user.backend = 'allauth.account.auth_backends.AuthenticationBackend' 
                login(request, request.user)  
                
            return redirect(f'http://{domain.domain}:{settings.PORT}/') 
        
    try:
        tenant_member = TenantMember.objects.get(user=request.user, tenant=request.tenant)
    except:
        tenant_member = None
        
    # get the list of tenants 
    
    if request.user.is_authenticated:
        user_tenants = TenantMember.objects.filter(user=request.user)
    else:
        user_tenants = None
    
    base_domain = f"{settings.BASE_URL}:{settings.PORT}"    
     
    if not hasattr(request, 'tenant'):
        template_name = 'home.html'
    else: 
        template_name = 'home_tenant.html' 
    
    context = {
        'tenant_form': tenant_form,
        'tenant_member': tenant_member,
        'user_tenants' : user_tenants,
        'base_domain' : base_domain
    }
    return render(request, template_name, context)


# def create_item(request):
#     if request.POST: 
#         name = request.POST.get('name')
#         item = Item(name=name)
#         item.save()
#         return HttpResponse(f'<li class="text-8xl font-thin">{item.name}</li>')

#     else:
#         return redirect('home')