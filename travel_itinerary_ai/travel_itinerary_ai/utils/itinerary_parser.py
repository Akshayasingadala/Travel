import re

def parse_itinerary(itinerary_text):
    """
    Parse the itinerary text into structured day data
    """
    days_breakdown = []
    
    # Split by day patterns (### Day 1:, ### Day 2:, etc.)
    day_pattern = r'###\s+Day\s+(\d+):\s*([^\n]+)'
    day_matches = list(re.finditer(day_pattern, itinerary_text, re.IGNORECASE))
    
    if not day_matches:
        return days_breakdown
    
    for idx, match in enumerate(day_matches):
        day_num = int(match.group(1))
        day_title = match.group(2).strip()
        
        # Get the content between this day and the next
        start_pos = match.end()
        if idx < len(day_matches) - 1:
            end_pos = day_matches[idx + 1].start()
        else:
            end_pos = len(itinerary_text)
        
        day_content = itinerary_text[start_pos:end_pos]
        
        # Extract location and cost
        location_match = re.search(r'\*\*Location:\*\*\s*([^\n]+)', day_content)
        location = location_match.group(1).strip() if location_match else None
        
        cost_match = re.search(r'\*\*Estimated Cost:\*\*\s*([^\n]+)', day_content)
        cost = cost_match.group(1).strip() if cost_match else None
        
        # Extract activities by time of day
        activities = []
        time_periods = ['morning', 'afternoon', 'evening', 'night', 'accommodation']
        
        for time_period in time_periods:
            # Look for **Morning:**, **Afternoon:**, etc.
            pattern = rf'\*\*{time_period.capitalize()}:\*\*([^*]+?)(?=\*\*|\Z)'
            time_match = re.search(pattern, day_content, re.IGNORECASE | re.DOTALL)
            
            if time_match:
                content = time_match.group(1)
                # Extract bullet points
                bullet_pattern = r'\*\s+\*\*([^*]+)\*\*:\s*([^*]+?)(?=\*\s\*\*|\Z)'
                bullets = re.findall(bullet_pattern, content)
                
                if bullets:
                    items = []
                    for bullet_title, bullet_content in bullets:
                        item_text = f"{bullet_title}: {bullet_content.strip()}"
                        items.append(item_text)
                    
                    if items:
                        activities.append({
                            'time': time_period,
                            'items': items
                        })
        
        day_data = {
            'day_num': day_num,
            'title': day_title,
            'location': location,
            'cost': cost,
            'activities': activities
        }
        
        days_breakdown.append(day_data)
    
    return days_breakdown
