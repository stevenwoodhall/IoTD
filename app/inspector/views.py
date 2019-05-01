from scapy.all import sniff, wrpcap
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import django_tables2 as tables
from .models import (PacketCapture)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from manager.models import Device
from os import remove


# Shows table of recent PacketCapture's
@login_required
def inspector_summary(request):

    class SimpleTable(tables.Table):
        class Meta:
            model = PacketCapture
            exclude = {'id'}
            template_name = 'django_tables2/bootstrap4.html'

    if request.method == 'POST':
        if request.POST.get('filterDevice') and request.POST.get('filterPcap'):
            pcap = get_object_or_404(PacketCapture,
                                     pk=request.POST.get('filterPcap'))
            targetMAC = request.POST.get('filterDevice')
            pkts = sniff(offline=pcap.file_path,
                         lfilter=lambda d: d.src == targetMAC)
            outPCAP = "/tmp/filtered.pcap"
            try:
                remove(outPCAP)
            except OSError:
                pass
            wrpcap(outPCAP, pkts)
            with open(outPCAP, 'rb') as pcapFile:
                response = HttpResponse(pcapFile.read())
                response['content_type'] = 'application/vnd.tcpdump.pcap'
                response['Content-Disposition'] = 'attachment;filename=' + \
                    pcap.filename()
                return response
        else:
            return redirect('/inspector/' + '?error=Invalid Filter')

    packet_captures = PacketCapture.objects.all().order_by('-dt_end')
    devices = Device.objects.all().order_by('title')

    return render(
        request,
        'inspector_summary.html',
        context={'page_title': 'Packet Inspector',
                 'packet_captures': packet_captures[0:12], 'devices': devices}
    )


# Returns a download for a given packet capture
@login_required
def inspector_capture(request, pk):
    pcap = get_object_or_404(PacketCapture, pk=pk)
    with open(pcap.file_path, 'rb') as pcapFile:
        response = HttpResponse(pcapFile.read())
        response['content_type'] = 'application/vnd.tcpdump.pcap'
        response['Content-Disposition'] = 'attachment;filename=' + \
            pcap.filename()
        return response


# Filters existing pcaps by MAC address using scapy
@login_required
def inspector_filter(request, pk):
    # pcap = get_object_or_404(PacketCapture, pk=pk)
    pkts = sniff(offline=inPCAP, lfilter=lambda d: d.src == targetMAC)
    outPCAP = ""
    wrpcap(outPCAP, pkts)

    with open(pcap.file_path, 'rb') as pcapFile:
        response = HttpResponse(pcapFile.read())
        response['content_type'] = 'application/vnd.tcpdump.pcap'
        response['Content-Disposition'] = 'attachment;filename=' + \
            pcap.filename()
        return response
