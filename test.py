from datetime import datetime

def getBatchTime():
    oldTime = datetime.strptime("2023-10-05 18:35", "%Y-%m-%d %H:%M")
    # oldTime = datetime.strptime(lastBatchTime, "%Y-%m-%d %H:%M")
    currentTime = datetime.now()
    
    oldTimeHourMinute = oldTime.strftime("%I.%M")
    currentTimeStr = currentTime.strftime("%Y-%m-%d %H:%M")
    currentTimeHourMinute = currentTime.strftime("%I.%M")

    try:
        timeDifference = currentTime - oldTime
    except:
        # configProps["last_batch_time"] = currentTimeStr
        # updateConfig(configFileName, configProps)
        return currentTimeHourMinute
    
    if timeDifference.total_seconds()/60 > 5:
        # configProps["last_batch_time"] = currentTimeStr
        # updateConfig(configFileName, configProps)
        return currentTimeHourMinute
    else:
        return oldTimeHourMinute
    
print(getBatchTime())