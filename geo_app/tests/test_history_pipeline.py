from datetime import date, datetime, timedelta


def generate_dates(start_date: date, end_date: date):
    current = start_date
    result = []
    while current <= end_date:
        result.append(current)
        current += timedelta(days=1)
    return result


def test_generate_dates_from_july_2026_to_today():
    start_date = date(2026, 7, 1)
    end_date = date(2026, 8, 2)
    dates = generate_dates(start_date, end_date)
    assert dates[0] == date(2026, 7, 1)
    assert dates[-1] == date(2026, 8, 2)
    assert len(dates) == 33
