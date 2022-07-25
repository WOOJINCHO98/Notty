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
    
#서울시 역코드로 지하철역별 열차 시간표 정보 검색 https://data.seoul.go.kr/dataList/OA-101/A/1/datasetView.do
api_url4 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchSTNTimeTableByIDService/1/5/0309/1/1/'




# Create your views here.
def home(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        searchword = request.POST.get('start')
        destword = request.POST.get('fin')
        if form.is_valid():
            #데이터 저장
            rt = Route()
            rt.start = request.POST['start']
            rt.fin = request.POST['fin']
            rt.save()
            
            
            
            ######################################
            
            #카카오 REST API KEY = 3ccf2a2e8eef7ee20af37e425477d818
            #출발 위치 좌표 잡기
            headers = {
                'Authorization': 'KakaoAK 3ccf2a2e8eef7ee20af37e425477d818',
            }

            params = {
                'page': '1',
                'size': '1',
                'sort': 'accuracy',
                'query': searchword+'역',
            }

            st_gps_response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', params=params, headers=headers)
            st_gps_resdata = st_gps_response.text
            st_gps_obj = json.loads(st_gps_resdata)
            st_gps_obj = st_gps_obj['documents']
            
            for item in st_gps_obj:
                st_gps_x = item.get('x')
                
            for item in st_gps_obj:
                st_gps_y = item.get('y')
            
            #도착 위치 좌표 잡기
            params = {
                'page': '1',
                'size': '1',
                'sort': 'accuracy',
                'query': destword+'역',
            }

            dest_gps_response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', params=params, headers=headers)
            dest_gps_resdata = dest_gps_response.text
            dest_gps_obj = json.loads(dest_gps_resdata)
            dest_gps_obj = dest_gps_obj['documents']
            
            for item in dest_gps_obj:
                dest_gps_x = item.get('x')
            
            for item in dest_gps_obj:
                dest_gps_y = item.get('y')
            
            
            
            #서울시 지하철역 정보 검색 (역명) https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do
            # 출발역 찾기
            api_url1 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/1/'+searchword+'/'
            response = requests.get(api_url1)
            resdata = response.text
            obj = json.loads(resdata)
            obj = obj['SearchInfoBySubwayNameService']
            obj = obj['row']
            # 도착역 찾기
            dest_api_url1 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/1/'+destword+'/'
            dest_response = requests.get(dest_api_url1)
            dest_resdata = dest_response.text
            dest_obj = json.loads(dest_resdata)
            dest_obj = dest_obj['SearchInfoBySubwayNameService']
            dest_obj = dest_obj['row']
            
            #지하철 경로 조회 서비스 (최소 시간) https://devming.tistory.com/214 |http://swopenAPI.seoul.go.kr/api/subway/인증Key값/요청데이터형식/OpenAPI 이름(서비스명)/요청 데이터 행 시작번호/요청 데이터 행 끝번호/출발역명/도착역명
            path_key = '646f7a76646a6f7733317842746455'
            path_api_url = 'http://swopenAPI.seoul.go.kr/api/subway/'+path_key+'/json/shortestRoute/0/5/'+searchword+'/'+destword
            path_response = requests.get(path_api_url)
            path_resdata = path_response.text
            path_obj = json.loads(path_resdata)
            path_obj = path_obj['shortestRouteList']
            
            #최소 시간 찾기
            path_time = ['999','999','999','999','999']
            
            i=0
            for time in path_obj:
                path_time[i] = time.get('shtTravelTm')
                i=i+1
            min_path_time = min(path_time)
            for item in path_obj:
                path_list = item.get('shtStatnNm')
                path_msg = item.get('shtTravelMsg')
                if min_path_time == item.get('shtTravelTm'):
                    break
                
            path_list = path_list.split(',')
            path_value_0 = path_list[0]

            
            
            '''
            #서울특별시_대중교통환승경로 조회 서비스 https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000414
            path_key = '1WiWiadJdsEUw9VTAe8%2BpAs4K39k6ulLAGzN%2BBDvLuUedlyrTLO%2FwKXqkXW%2FEuTRT%2FLepS1etUJeBAyOvq9xVg%3D%3D'
            path_api_url = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway?ServiceKey='+path_key+'&startX='+st_gps_x+'&startY='+st_gps_y+'&endX='+dest_gps_x+'&endY='+dest_gps_y+'&resultType=json'
            path_response = requests.get(path_api_url)
            path_resdata = path_response.text
            path_obj = json.loads(path_resdata)
            path_obj = path_obj['msgBody']
            path_obj = path_obj['itemList']
            for item in path_obj:
                path_list = item.get('pathList')
            '''
            #서울교통공사_서울 도시철도 목적지 경로정보 https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15097640
            '''
            key = 'oTsloDJ6xmHymJiItQxmn1GEp2HiiX+8fA+H6PRKbCUp3XWPNEAViCpeWOir0YPCRpFHH3XQ6i6PlYwNdEg4dQ=='

            
            api_url4 = 'http://apis.data.go.kr/B553766/smt-path/path'
            params ={'serviceKey' : key, 'pageNo' : '1', 'numOfRows' : '10', 'dept_station_code' : '2728', 'dest_station_code' : '0214', 'week' : 'DAY', 'search_type' : 'FASTEST', 'first_last' : '', 'dept_time' : '120001', 'train_seq' : '' }

            path_response = requests.get(api_url4, params=params)
            path_resdata = path_response.text
            path_obj = json.loads(path_resdata)
            path_obj = path_obj['data']
            '''
            #http://apis.data.go.kr/B553766/smt-path/path?serviceKey=oTsloDJ6xmHymJiItQxmn1GEp2HiiX%2B8fA%2BH6PRKbCUp3XWPNEAViCpeWOir0YPCRpFHH3XQ6i6PlYwNdEg4dQ%3D%3D&numOfRows=10&pageNo=1&dept_station_code=0222&dest_station_code=4117&week=DAY
            
            #서울교통공사 실시간 도착 정보
            api_url3 = 'http://swopenAPI.seoul.go.kr/api/subway/'+key_num+'/json/realtimeStationArrival/0/1/'+destword
            response2 = requests.get(api_url3)
            findata = response2.text
            finobj = json.loads(findata)
            finobj = finobj['realtimeArrivalList']
            
            #############################################
            return render(request,'detail.html',{'obj' : obj,'path_msg':path_msg,'min_path_time':min_path_time,'path_time':path_time,'path_list':path_list,'path_obj':path_obj,'dest_obj':dest_obj , 'finobj' : finobj})
    else:
        form = RouteForm()



    return render(request, 'home.html', {'form' : form})


def setting(request):
    return render(request, 'setting.html')


def detail(request):
    

    return render(request, 'detail.html')


def favorite(request):
    return render(request, 'favorite.html')