import json, os
from datetime import datetime, timedelta
from urllib.request import Request, urlopen  # Python 3


# try:
#     from urllib.request import Request, urlopen  # Python 3
# except ImportError:
#     from urllib2 import Request, urlopen  # Python 2


def convertTime(salatTime, offset):
    salatTime = datetime.strptime(salatTime, '%I:%M %p')
    # salatTime = datetime.strptime(salatTime, '%H:%M')
    salatTime = salatTime + timedelta(hours=0, minutes=offset)
    salatTime = datetime.strftime(salatTime, '%H:%M')
    return salatTime


def useOtherApi():
    location = "baltimore,md"
    apiKey = "1383220a5e440a4e2b47623ddde2b6fa91"  # http://muslimsalat.com/api/#key
    url = "http://muslimsalat.com/" + location + "/daily.json?key=" + apiKey

    req = Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/json')
    response = urlopen(req).read().decode('utf-8')

    jsonString = json.loads(response)

    times = jsonString['items'][0]

    fajr = convertTime(times['fajr'], 0)
    dhuhr = convertTime(times['dhuhr'], 0)
    asr = convertTime(times['asr'], 0)
    maghrib = convertTime(times['maghrib'], -5)
    isha = convertTime(times['isha'], 0)

    timings = {
        'fajr': fajr,
        'dhuhr': dhuhr,
        'asr': asr,
        'maghrib': maghrib,
        'isha': isha
    }

    return timings

def useMyApi():
    api_calendar_pre = 'http://api.aladhan.com/v1/calendarByCity?'
    api_day_pre = 'https://api.aladhan.com/v1/timingsByCity?'
    api_method = '&method=2&school=2'
    api_school = '&school=1'

    zipcode = '97078'
    city = 'Beaverton'
    state = 'Oregon'
    country = 'United States'

    api_city = 'city=' + zipcode
    api_country = '&country=United%20States'

    api_day = api_day_pre + api_city + api_country + api_method + api_school

    print(api_day)
    req = Request(api_day)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/json')
    response = urlopen(req).read().decode('utf-8')

    jsonString = json.loads(response)

    # print(jsonString)

    times = jsonString['data']['timings']

    # print(times)

    fajr = times['Fajr']
    dhuhr = times['Dhuhr']
    asr = times['Asr']
    maghrib = times['Maghrib']
    isha = times['Isha']

    timings = {
        'fajr': fajr,
        'dhuhr': dhuhr,
        'asr': asr,
        'maghrib': maghrib,
        'isha': isha
    }

    return timings



def useBilalScrape():
    os.system("cd bilalscraper/ && scrapy crawl prayertimebot")

    with open('bilalscraper/timings.json') as json_data:
        timing_dct = json.loads(json_data.read())
        print(timing_dct)

    timings_adhan = {
        'fajr': convertTime(timing_dct['Fajr']['adhan'] + ' AM', 0),
        'dhuhr': convertTime(timing_dct['Duhr']['adhan'] + ' PM', 0),
        'asr': convertTime(timing_dct['Asr']['adhan'] + ' PM', 0),
        'maghrib': convertTime(timing_dct['Maghrib']['adhan'] + ' PM', 0),
        'isha': convertTime(timing_dct['Isha']['adhan'] + ' PM', 0),
    }

    timings_iqamah = {
        'fajr': convertTime(timing_dct['Fajr']['iqamah'] + ' AM', -5),
        'dhuhr': convertTime(timing_dct['Duhr']['iqamah'] + ' PM', -5),
        'asr': convertTime(timing_dct['Asr']['iqamah'] + ' PM', -5),
        'maghrib': convertTime(timing_dct['Maghrib']['iqamah'] + ' PM', -5),
        'isha': convertTime(timing_dct['Isha']['iqamah'] + ' PM', -5),
    }

    #
    # print("Adhan: " + str(timings_adhan))
    # print("Iqamah: " + str(timings_iqamah))

    # return timings_adhan
    return timings_iqamah

def useBilalHTML():
    url = 'http://www.bilalmasjid.com/'

    req = Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'})

    html = urlopen(req).read().decode('utf-8')

    fajr = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_Fajr">')[1].split('</span>')[0]
    fajr_iqamah = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_FajrIqama">')[1].split('</span>')[0]

    dhuhr = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_Duhr">')[1].split('</span>')[0]
    dhuhr_iqamah = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_DuhrIqama">')[1].split('</span>')[0]

    asr = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_Asr">')[1].split('</span>')[0]
    asr_iqamah = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_AsrIqama">')[1].split('</span>')[0]

    maghrib = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_Maghrib">')[1].split('</span>')[0]
    maghrib_iqamah = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_MaghribIqama">')[1].split('</span>')[0]

    isha = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_Isha">')[1].split('</span>')[0]
    isha_iqamah = html.strip().split('ctl00_ctl00_cphContent_PrayerTimes1_IshaIqama">')[1].split('</span>')[0]



    timings_adhan = {
        'fajr': convertTime(fajr + ' AM', -5),
        'dhuhr': convertTime(dhuhr + ' PM', -5),
        'asr': convertTime(asr + ' PM', -5),
        'maghrib': convertTime(maghrib + ' PM', -5),
        'isha': convertTime(isha + ' PM', -5),
    }

    timings_iqamah = {
        'fajr': convertTime(fajr_iqamah + ' AM', -5),
        'dhuhr': convertTime(dhuhr_iqamah + ' PM', -5),
        'asr': convertTime(asr_iqamah + ' PM', -5),
        'maghrib': convertTime(maghrib_iqamah + ' PM', -5),
        'isha': convertTime(isha_iqamah + ' PM', -5),
    }

    # print("Adhan: " + str(timings_adhan))
    # print("Iqamah: " + str(timings_iqamah))


    # return timings_adhan
    return timings_iqamah


# timings = useOtherApi()
# timings = useMyApi()
# timings = useBilalScrape()
timings = useBilalHTML()

print("Timings: " + str(timings))

DOMAIN = 'salat_times'


def setup(hass, config):
    hass.states.set('salat.fajr', timings['fajr'])
    hass.states.set('salat.dhuhr', timings['dhuhr'])
    hass.states.set('salat.asr', timings['asr'])
    hass.states.set('salat.maghrib', '19:33')
    hass.states.set('salat.isha', timings['isha'])

    return True