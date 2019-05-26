import appdaemon.plugins.hass.hassapi as hass
import json, os
import datetime
from datetime import timedelta
from urllib.request import Request, urlopen  # Python 3



#
# Hellow World App
#
# Args:
#

class SalatTimes(hass.Hass):

    def initialize(self):
        self.log("Hello from SalatTimes, this is AK")
        
        self.setSalatTimes(None)
        
        # Create a time object for 1am
        time = datetime.time(2, 0, 0)
        # Schedule a daily callback that will call run_daily() at 7pm every night
        self.run_daily(self.setSalatTimes, time)

    def setSalatTimes(self, kwargs):
        
        # timings = self.useOtherApi()
        # timings = self.useMyApi()
        # timings = self.useBilalScrape()
        timings = self.useBilalHTML()
        
        self.set_state('salat.fajr', state = timings['fajr'])
        self.set_state('salat.dhuhr', state = timings['dhuhr'])
        self.set_state('salat.asr', state = timings['asr'])
        self.set_state('salat.maghrib', state = timings['maghrib'])
        self.set_state('salat.isha', state = timings['isha'])
        
        end_timings = self.getEndTimes()
        print(f'end_timings: {end_timings}')
        
        self.set_state('salat.fajr_end', state = end_timings['fajr_end'])
        self.set_state('salat.dhuhr_end', state = end_timings['dhuhr_end'])
        self.set_state('salat.asr_end', state = end_timings['asr_end'])
        self.set_state('salat.maghrib_end', state = end_timings['maghrib_end'])
        self.set_state('salat.isha_end', state = end_timings['isha_end'])
        
        self.log("Saved Salat times for day: " + str(self.date()))

    def convertTime(self, salatTime, offset):
        salatTime = datetime.datetime.strptime(salatTime, '%I:%M %p')
        # salatTime = datetime.datetime.strptime(salatTime, '%H:%M')
        salatTime = salatTime + timedelta(hours=0, minutes=offset)
        salatTime = datetime.datetime.strftime(salatTime, '%H:%M')
        return salatTime
        
    def addOffset(self, salatTime, offset):
        salatTime = datetime.datetime.strptime(salatTime, '%H:%M')
        salatTime = salatTime + timedelta(hours=0, minutes=offset)
        salatTime = datetime.datetime.strftime(salatTime, '%H:%M')
        return salatTime


    def useOtherApi(self):
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


    def getEndTimes(self):
        api_calendar_pre = 'http://api.aladhan.com/v1/calendarByCity?'
        api_day_pre = 'https://api.aladhan.com/v1/timingsByCity?'
        api_method = '&method=2'
        api_school = '&school=0'

        zipcode = '97078'
        city = 'Beaverton'
        state = 'Oregon'
        country = 'United States'

        api_city = 'city=' + zipcode
        api_country = '&country=United%20States'

        api_day = api_day_pre + api_city + api_country + api_method + api_school

        # print(api_day)
        req = Request(api_day)
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        response = urlopen(req).read().decode('utf-8')

        jsonString = json.loads(response)

        times = jsonString['data']['timings']

        # print(f'times: {times}')

        end_timings = {
            'fajr_end': self.addOffset(times['Sunrise'], -15),
            'dhuhr_end': self.addOffset(times['Asr'], -15),
            'asr_end': self.addOffset(times['Maghrib'], -15),
            'maghrib_end': self.addOffset(times['Isha'], -15),
            'isha_end': self.addOffset(times['Midnight'], -15)
        }
        
        return end_timings


    def useMyApi(self):
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

    def useBilalScrape(self):
        os.system("cd bilalscraper/ && scrapy crawl prayertimebot")

        with open('bilalscraper/timings.json') as json_data:
            timing_dct = json.loads(json_data.read())
            print(timing_dct)

        timings_adhan = {
            'fajr': self.convertTime(timing_dct['Fajr']['adhan'] + ' AM', 0),
            'dhuhr': self.convertTime(timing_dct['Duhr']['adhan'] + ' PM', 0),
            'asr': self.convertTime(timing_dct['Asr']['adhan'] + ' PM', 0),
            'maghrib': self.convertTime(timing_dct['Maghrib']['adhan'] + ' PM', 0),
            'isha': self.convertTime(timing_dct['Isha']['adhan'] + ' PM', 0),
        }

        timings_iqamah = {
            'fajr': self.convertTime(timing_dct['Fajr']['iqamah'] + ' AM', -5),
            'dhuhr': self.convertTime(timing_dct['Duhr']['iqamah'] + ' PM', -5),
            'asr': self.convertTime(timing_dct['Asr']['iqamah'] + ' PM', -5),
            'maghrib': self.convertTime(timing_dct['Maghrib']['iqamah'] + ' PM', -5),
            'isha': self.convertTime(timing_dct['Isha']['iqamah'] + ' PM', -5),
        }

        #
        # print("Adhan: " + str(timings_adhan))
        # print("Iqamah: " + str(timings_iqamah))

        # return timings_adhan
        return timings_iqamah

    def useBilalHTML(self):
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
            'fajr': self.convertTime(fajr + ' AM', -5),
            'dhuhr': self.convertTime(dhuhr + ' PM', -5),
            'asr': self.convertTime(asr + ' PM', -5),
            'maghrib': self.convertTime(maghrib + ' PM', -5),
            'isha': self.convertTime(isha + ' PM', -5),
        }

        timings_iqamah = {
            'fajr': self.convertTime(fajr_iqamah + ' AM', -5),
            'dhuhr': self.convertTime(dhuhr_iqamah + ' PM', -5),
            'asr': self.convertTime(asr_iqamah + ' PM', -5),
            'maghrib': self.convertTime(maghrib_iqamah + ' PM', -5),
            'isha': self.convertTime(isha_iqamah + ' PM', -5),
        }

        # print("Adhan: " + str(timings_adhan))
        # print("Iqamah: " + str(timings_iqamah))


        # return timings_adhan
        return timings_iqamah
