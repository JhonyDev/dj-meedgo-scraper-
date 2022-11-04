import datetime

from django.db.models import Q


def get_api_exception(detail, code):
    from rest_framework.exceptions import APIException
    api_exception = APIException()
    api_exception.status_code = code
    api_exception.detail = detail
    print(detail)
    return api_exception


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        from datetime import timedelta
        yield start_date + timedelta(n)


def days_between(d1, d2):
    from dateutil import parser
    d1 = parser.parse(str(d1))
    d2 = parser.parse(str(d2))
    return abs(d2 - d1).days


def get_availability(date, end_date):
    from .models import Booking, Room, Category
    parent_dict = {"Total": 0}
    date = date + datetime.timedelta(days=1)
    end_date = end_date - datetime.timedelta(days=1)
    category = Category.objects.all()
    for cat in category:
        parent_dict[cat.name] = 0

    bookings = Booking.objects.filter(
        Q(check_in_date__range=[date, end_date]) | Q(check_out_date__range=[date, end_date]) |
        (Q(check_in_date__lt=date) & Q(check_out_date__gt=end_date))
    )

    rooms = Room.objects.all()
    parent_dict["Total"] = rooms.count()

    for room in rooms:
        parent_dict[room.category.name] = {}
        parent_dict[room.category.name]["count"] = Room.objects.filter(category__name=room.category.name).count()
        parent_dict[room.category.name]["cost_per_night"] = room.category.cost_per_night

    for booking in bookings:
        for room in booking.rooms.all():
            parent_dict[room.category.name]["count"] = parent_dict[room.category.name]["count"] - 1
            parent_dict["Total"] = parent_dict['Total'] - 1

    return parent_dict


def get_target_dates(month, year):
    from dateutil import parser
    target_start_date = f'{year}-{month}-01'
    try:
        target_end_date = f'{year}-{month}-30'
    except:
        try:
            target_end_date = f'{year}-{month}-29'
        except:
            target_end_date = f'{year}-{month}-28'
    target_end_date = parser.parse(target_end_date)
    target_start_date = parser.parse(target_start_date)
    return target_start_date, target_end_date


def generate_pdf_get_path(url):
    import pdfkit

    # path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    import uuid
    id_ = uuid.uuid4().hex
    try:
        # pdfkit.from_url(url, f'media/{id_}.pdf', configuration=config)
        pdfkit.from_url(url, f'media/{id_}.pdf')
    except Exception as e:
        print(str(e))
    return f'media/{id_}.pdf'


def encode_base_64(url):
    with open(f"{url}", "rb") as pdf_file:
        import base64
        encoded_string = str(base64.b64encode(pdf_file.read()))
        encoded_string = encoded_string.replace(encoded_string[0], "", 1)
        encoded_string = encoded_string.replace(encoded_string[0], "", 1)
        encoded_string = encoded_string.replace(encoded_string[-1], "", 1)
        return encoded_string
