# scripts/add_demo_data.py
from datetime import datetime
from inspector.models import PacketCapture
from os import path


def run(*args):
    if args:
        fileName = path.basename(args[0])
        startDate = datetime.strptime(fileName.split(".")[0], "%d-%m-%Y_%H:%M")
        PacketCapture.objects.get_or_create(dt_start=startDate,
                                            dt_end=datetime.now(),
                                            file_path=args[0],
                                            file_size=args[1])
