from datetime import date,timedelta

def day_window(day: date) -> tuple[str,str]:
    return day.isoformat()+" 00:00:00",(day+timedelta(days=1)).isoformat()+" 00:00:00"
