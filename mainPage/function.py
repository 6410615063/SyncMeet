from mainPage.models import Activity

# need: 2dList[day][hour] telling if each slot is free or not
def getTableSlot(activities):
    # False(0) = free, True(1) = busy
    DAY_NUMBER = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
    }
    table_slot = [[0 for col in range(24)] for row in range(7)]
    for activity in activities:
        # start, start_day, end, end_day
        start_day_num = DAY_NUMBER[activity.start_day]
        end_day_num = DAY_NUMBER[activity.end_day]
        start_hour = activity.start.hour
        end_hour = activity.end.hour

        if((start_day_num == end_day_num) and (start_hour <= end_hour)):
            for hour in range(start_hour, min(23, end_hour) + 1, 1):
                table_slot[start_day_num][hour] += 1
        else:
            for hour in range(start_hour, 24, 1):
                table_slot[start_day_num][hour] += 1
            for hour in range(end_hour + 1):
                table_slot[end_day_num][hour] += 1

            day = (start_day_num + 1) % 7
            while(day != end_day_num):
                for hour in range(24):
                    table_slot[day][hour] = 1
                day = (day + 1) % 7

    # for row in table_slot:
    #     print(row)

    return table_slot
