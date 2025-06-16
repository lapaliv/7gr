from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from django.template.response import TemplateResponse
from climate.container import Container
from climate.models import Sector
import math

@staff_member_required
def digital_twin(request):
    limit = 50

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    offset = (page - 1) * limit

    sector_repository = Container.sector_repository()
    device_repository = Container.device_repository()

    sectors = sector_repository.get_all(offset = offset, limit = limit)
    total_sectors = sector_repository.count()
    total_pages = math.ceil(total_sectors / limit)

    grouped_devices = {}

    for sector in sectors:
        sector_devices = device_repository.get_for_sector(sector = sector)
        grouped_devices[sector.id] = sector_devices

    return TemplateResponse(request, "admin/digital_twin.html", {
        "title": "Digital twin",
        "sectors": sectors,
        "grouped_devices": grouped_devices,
        "page": page,
        "total_pages": total_pages,
        "limit": limit,
    })
