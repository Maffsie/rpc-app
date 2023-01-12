#base /v1/functions/time
#/
## returns epoch
#/in/<string:locale>
## returns string f"it is currently {yyyy-mm-dd HH:MM:SS} in {locale} my dudes"
#/json
## returns json {"epoch":1673482571336,"DTZ":"2023-01-12T00:16:11.336Z","hr":{"time":"00:16","timep":"00:16 AM","times":"00:16:11","timesp":"00:16:11 AM","date":"Thu 12, Jan 2023"},"raw":{"mil":336,"sec":11,"min":16,"hrs":0,"day":"Thu","dom":12,"mon":"Jan","mth":1,"yrs":2023}}
#/json/deskclock
## returns json {"epoch":1673482776744,"hr":{"time":"00:19","times":"00:19:36","date":"Thu 12, Jan 2023"},"strings":{}}
#/text
## returns string f"{HH:MM:SS AM/PM}"