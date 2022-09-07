def get_api_exception(detail, code):
    from rest_framework.exceptions import APIException
    api_exception = APIException()
    api_exception.status_code = code
    api_exception.detail = detail
    print(detail)
    return api_exception


def get_availability(date):
    from .models import Booking, Room
    bookings = Booking.objects.filter(check_in_date__gte=date, check_out_date__lt=date)
    booked_rooms = []
    for booking in bookings:
        for room in booking.rooms:
            booked_rooms.append(room.pk)
    rooms = Room.objects.all().exclude(pk__in=booked_rooms)
    return rooms


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
