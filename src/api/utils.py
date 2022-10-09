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
    end_date = end_date - datetime.timedelta(days=1)
    category = Category.objects.all()
    for cat in category:
        parent_dict[cat.name] = 0

    bookings = Booking.objects.filter(
        Q(check_in_date__range=[date, end_date]) | Q(check_out_date__range=[date, end_date]) |
        (Q(check_in_date__lt=date) & Q(check_out_date__gt=end_date))
    )
    booked_rooms = []
    for booking in bookings:
        for room in booking.rooms.all():
            if room is not None:
                if room.pk not in booked_rooms:
                    booked_rooms.append(room.pk)

    rooms = Room.objects.all().exclude(pk__in=booked_rooms)
    booked_rooms_query = Room.objects.filter(pk__in=booked_rooms)
    parent_dict["Total"] = rooms.count()

    for room in rooms:
        cat = parent_dict.get(room.category.name)
        if cat is None:
            parent_dict[room.category.name] = 0
        cat = parent_dict.get(room.category.name)
        parent_dict[room.category.name] = cat + 1
    #
    # for room in booked_rooms_query:
    #     parent_dict[room.category.name] = parent_dict[room.category.name] - 1
    #     parent_dict["Total"] = parent_dict['Total'] - 1

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
