from datetime import time
from django.db.models import Q
from django.db.models.functions import ExtractWeekDay

def filter_events(queryset, campus=None, days=None, time_ranges=None, event_types=None):
    events = list(queryset)
    
    if campus:
       events = [e for e in events if e.campus in campus]            
    
    if event_types:
        events = [e for e in events if e.event_type in event_types]
        
    if days: 
        day_map = {'Sunday': 6, 'Monday' :0, 'Tuesday' :1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5}
        target_days = [day_map[d] for d in days if d in day_map]
        events = [e for e in events if e.date.weekday() in target_days]    
        
    if time_ranges:
        filtered = []
        for event in queryset:
            dt_start_time = event.start_time_obj
            dt_end_time = event.end_time_obj
            if not dt_start_time or not dt_end_time:
                continue
            if 'Morning' in time_ranges and dt_start_time >= time(8,0) and dt_start_time < time(12,0):
                filtered.append(event)
            elif 'Afternoon' in time_ranges and dt_start_time >= time(12,0) and dt_start_time < time(17,0):
                filtered.append(event)
            elif 'Evening' in time_ranges and dt_start_time >= time(17,0):
                filtered.append(event)
        events = filtered             
    
    return events