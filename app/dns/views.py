from django.shortcuts import render
import validators
from django.contrib.auth.decorators import login_required
from .models import (BlockedDomains, DNSQuery, HiddenDomains)
from django.db.models import Count
import django_tables2 as tables
import subprocess
from django.http import Http404
from django.shortcuts import redirect


@login_required
def test(request):
    """
    View function for DNS dashboard.
    """
    try:
        top_requests = DNSQuery.objects.all().filter(record='A').values(
            'domain', 'record').annotate(total=Count('domain')).order_by(
            '-total')

        class SimpleTable(tables.Table):
            class Meta:
                model = DNSQuery
                exclude = {'id', 'src'}
                template_name = 'django_tables2/bootstrap4.html'

        queryset = DNSQuery.objects.all().order_by('-datetime')

        table = SimpleTable(queryset)
        table.paginate(page=request.GET.get('page', 1), per_page=15)

        blocked = BlockedDomains.objects.all().values('domain')
        banner = None

        # Block and Hide Domains
        if request.GET.get('block-domain'):
            domain = request.GET.get('block-domain')
            # Check if valid domain
            if validators.domain(domain):
                # Check if already blocked else block
                try:
                    blocked = BlockedDomains.objects.get(domain=domain)
                    banner = {'title': 'Domain Already Blocked',
                              'type': 'warning', 'msg': 'The domain "{}"'
                              ' is already blocked.'.format(domain)}
                except BlockedDomains.DoesNotExist:
                    blocked = BlockedDomains(domain=domain)
                    blocked.save()
                    try:
                        with open("/opt/iotd/app/dns/hosts-blocklists/"
                                  "domains.txt", "a") as hostfile:
                            hostfile.write(
                                "address=/{}/0.0.0.0\n".format(domain))
                            hostfile.write("address=/{}/::\n".format(domain))
                            subprocess.call(
                                ["sudo service dnsmasq restart"], shell=True)
                            banner = {'title': 'Domain Blocked',
                                      'type': 'warning',
                                      'msg': 'The domain "{}" '
                                      'has been blocked.'.format(domain)}
                    except:
                        banner = {'title': 'Blocking Failed', 'type': 'danger',
                                  'msg': 'Failed to block'
                                  ' domain "{}".'.format(domain)}
            else:
                banner = {'title': 'Invalid Domain', 'type': 'danger',
                          'msg': 'The domain "{}" is invalid.'.format(domain)}

        return render(
            request,
            'summary.html', context={'page_title': 'DNS Detective',
                                     'banner': banner, 'dns_requests': table,
                                     'top_requests': top_requests[:15]}
        )
    except Exception as e:
        print(e)
        return render(request, 'summary.html')


@login_required
def clear_dns(request):
    try:
        ip = request.GET.get('ip')
        queries = DNSQuery.objects.filter(src=ip)
        queries.delete()
        return redirect('/dns/')
    except Exception as e:
        raise Http404(e)
