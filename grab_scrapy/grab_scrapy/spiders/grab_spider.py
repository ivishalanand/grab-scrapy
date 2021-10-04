import json
import time

import pandas as pd
import scrapy
from bs4 import BeautifulSoup
from pypasser import reCaptchaV3


class Spider(scrapy.Spider):
    name = "grab"

    def get_reCaptcha_response(self):
        ANCHOR_URL = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lebb64UAAAAAImxDKfLwMMFuVit2Rq3KBZD-BHl&co' \
                     '=aHR0cHM6Ly9mb29kLmdyYWIuY29tOjQ0Mw..&hl=en&v=-TriQeni1Ls-Mdq_ssN2cUL5&size=invisible&cb' \
                     '=v568j8wdun88'
        reCaptcha_response = reCaptchaV3(ANCHOR_URL)
        return reCaptcha_response

    def get_headers(self):
        headers = {
            "authority": "portal.grab.com",
            "accept-language": "en",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-recaptcha-token": self.get_reCaptcha_response(),
            "x-country-code": "PH",
            "x-grab-web-app-version": "8TF_lsXpCd5W~La6fUN~5",
            "x-gfc-country": "PH",
            "sec-gpc": "1",
            "origin": "https://food.grab.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://food.grab.com/"
        }
        return headers

    def start_requests(self):
        start_urls = ['https://portal.grab.com/foodweb/v2/search'] * 15

        offset = 32
        for url in start_urls:
            body = '{"latlng":"14.523859,120.992159","keyword":"","offset":%s,"pageSize":32,"countryCode":"PH"}' % offset
            headers = self.get_headers()
            yield scrapy.Request(
                url=url,
                method='POST',
                dont_filter=True,
                headers=headers,
                body=body)
            print("Offset: {}".format(offset))
            offset = offset + 32
            print("----" * 10)

    def parse(self, response):
        time.sleep(2)
        collector = []
        soup = BeautifulSoup(response.body, "html.parser")
        contents = json.loads(soup.contents[0])
        data_list = contents["searchResult"]["searchMerchants"]
        for data in data_list:
            latitude = data["latlng"]["latitude"]
            longitude = data["latlng"]["longitude"]
            name = data["address"]["name"]
            print(name, " | ", latitude, " | ", longitude)
            collector.append([name, latitude, longitude])

        try:
            df = pd.DataFrame(collector, columns=["Restaurant", "Latitude", "Longitude"])
            df_prev = pd.read_csv("lat_long.csv")
            df_new = pd.concat([df, df_prev]).drop_duplicates()

            print("Saved the loaded Restaurants location")
            df_new.to_csv("lat_long.csv", index=False)
        except:
            df = pd.DataFrame(collector, columns=["Restaurant", "Latitude", "Longitude"])
            df.drop_duplicates()
            df.to_csv("lat_long.csv", index=False)

