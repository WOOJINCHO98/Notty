from tracemalloc import start
from urllib import response
from django.shortcuts import render, redirect
import requests
from .forms import RouteForm
from .models import Route
import json



key_num = '646f7a76646a6f7733317842746455'

#서울교통공사 노선별 지하철역 정보
api_url2 = 'http://openapi.seoul.go.kr:8088/'+key_num+'/json/SearchSTNBySubwayLineInfo/1/100/'
#서울교통공사 실시간 도착 정보
api_url3 = 'http://swopenAPI.seoul.go.kr/api/subway/'+key_num+'/json/realtimeStationArrival/0/5/서울'
#서울시 역코드로 지하철역별 열차 시간표 정보 검색 https://data.seoul.go.kr/dataList/OA-101/A/1/datasetView.do
api_url4 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchSTNTimeTableByIDService/1/5/0309/1/1/'










# Create your views here.
def home(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        searchword = request.POST.get('start')
        if form.is_valid():
            #데이터 저장
            rt = Route()
            rt.start = request.POST['start']
            rt.fin = request.POST['fin']
            rt.save()
            
            #서울시 지하철역 정보 검색 (역명) https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do
            api_url1 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+searchword+'/'
            response = requests.get(api_url1)
            resdata = response.text
            obj = json.loads(resdata)
            obj = obj['SearchInfoBySubwayNameService']
            return render(request,'detail.html',{'obj' : obj})
    else:
        form = RouteForm()



    return render(request, 'home.html', {'form' : form})


def setting(request):
    return render(request, 'setting.html')


def detail(request):


    return render(request, 'detail.html')


def favorite(request):
    return render(request, 'favorite.html')