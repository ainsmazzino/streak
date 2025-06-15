from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Activity, CustomUser
import datetime


@login_required
def home(request):
    today = timezone.now().date()
    has_checked_in = Activity.objects.filter(user=request.user, date=today).exists()

    if request.method == "POST" and not has_checked_in:
        note = request.POST.get("note", "")
        Activity.objects.create(user=request.user, note=note)
        request.user.update_streak()
        request.user.points += 1
        request.user.consecutive_misses = 0
        request.user.save()
        return redirect("home")

    return render(request, "core/home.html", {"has_checked_in": has_checked_in})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Activity, CustomUser
import datetime
from datetime import timedelta
from collections import OrderedDict

import pytz


@login_required
def reports(request):
    # today = timezone.now().date()
    india_tz = pytz.timezone("Asia/Kolkata")
    today = timezone.now().astimezone(india_tz).date()
    start_date = today - timedelta(days=365)
    users = CustomUser.objects.all()

    # Generate month ranges
    month_ranges = OrderedDict()
    current = start_date
    while current <= today:
        month_key = current.strftime("%Y-%m")
        month_name = current.strftime("%b %Y")
        if month_key not in month_ranges:
            month_ranges[month_key] = {
                "name": month_name,
                "start": current.replace(day=1),
                "end": (current.replace(day=28) + timedelta(days=4)).replace(day=1)
                - timedelta(days=1),
                "days": [],
            }
        current += timedelta(days=1)

    # Prepare user data
    user_data = []
    for user in users:
        activities = set(
            Activity.objects.filter(
                user=user, date__range=[start_date, today]
            ).values_list("date", flat=True)
        )

        user_calendar = []
        for month_key, month_info in month_ranges.items():
            month_days = []
            current_day = month_info["start"]
            while current_day <= month_info["end"]:
                if start_date <= current_day <= today:
                    status = (
                        "present"
                        if current_day in activities
                        else ("absent" if current_day < today else "future")
                    )
                    month_days.append(
                        {"date": current_day, "day": current_day.day, "status": status}
                    )
                current_day += timedelta(days=1)

            user_calendar.append({"month_name": month_info["name"], "days": month_days})

        user_data.append({"user": user, "calendar": user_calendar})

    return render(
        request,
        "core/reports.html",
        {"user_data": user_data, "today": today, "start_date": start_date},
    )


@login_required
def profile(request):
    user = request.user
    today = timezone.now().date()

    # Apply penalties for missed days
    if user.last_checkin and user.last_checkin < today:
        days_missed = (today - user.last_checkin).days

        if days_missed > 0:
            user.consecutive_misses += days_missed

            if user.consecutive_misses == 1:
                user.points *= 0.75  # 25% penalty
            elif user.consecutive_misses == 2:
                user.points *= 0.5  # 50% penalty
            elif user.consecutive_misses >= 3:
                user.points = 0  # Reset points

            user.save()

    return render(request, "core/profile.html")
