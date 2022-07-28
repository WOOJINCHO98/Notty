from tracemalloc import start
from urllib import response
from xml.dom.minidom import Attr
from django.shortcuts import render, redirect
import requests
from .forms import RouteForm
from .models import Route
import json

key_num = '646f7a76646a6f7733317842746455'
    

#서울시 역코드로 지하철역별 열차 시간표 정보 검색 https://data.seoul.go.kr/dataList/OA-101/A/1/datasetView.do
api_url4 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchSTNTimeTableByIDService/1/5/0309/1/1/'

'''
화면에 표시 할 자료
line : 처음 탄 지하철의 호선
sht_path_list : 최단 시간 경로
min_path_list : 최소 환승 경로

trans_line : 1회 환승 한 이후 지하철의 호선(최단시간)
trans_station : 1회 환승 한 지하철역(최단시간)
joined_path_station_list : 출발지부터 1회 환승 전 까지의 경로(최단시간)
after_trans_path_list : 1회 환승 이후 지하철 경로(최단시간)
---------------------------------------------------
min_after_trans_path_list : 1회 환승 이후 지하철 경로(최소환승)
'''

trans_line = ''

min_trans_line = ''
after_trans_path_list = ''
min_after_path_list =''
min_joined_path_station_list = ''
joined_path_station_list = ''
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
            
            global min_trans_line
            min_trans_line=''
            global after_trans_path_list
            after_trans_path_list = ''
            global min_after_trans_path_list
            min_after_trans_path_list =''
            global min_joined_path_station_list
            min_joined_path_station_list = ''
            global joined_path_station_list
            joined_path_station_list =''
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

            global trans_line
            #서울특별시_대중교통환승경로 조회 서비스 https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000414
            trans_path_key = '1WiWiadJdsEUw9VTAe8%2BpAs4K39k6ulLAGzN%2BBDvLuUedlyrTLO%2FwKXqkXW%2FEuTRT%2FLepS1etUJeBAyOvq9xVg%3D%3D'
            trans_path_api_url = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway?ServiceKey='+trans_path_key+'&startX='+st_gps_x+'&startY='+st_gps_y+'&endX='+dest_gps_x+'&endY='+dest_gps_y+'&resultType=json'
            trans_path_response = requests.get(trans_path_api_url)
            trans_path_resdata = trans_path_response.text
            trans_path_obj1 = json.loads(trans_path_resdata)
            trans_path_obj = trans_path_obj1['msgBody']
            trans_path_obj = trans_path_obj['itemList']
            trans_path_list = []
            for item in trans_path_obj:
                trans_path_list = item.get('pathList')
            
            print(trans_path_list)
            print('\n\n\n')
            print('테스트텟트\n')
            print(trans_path_obj1)
            
            
            

            #지하철 경로 조회 서비스 (최단 시간) https://devming.tistory.com/214 |http://swopenAPI.seoul.go.kr/api/subway/인증Key값/요청데이터형식/OpenAPI 이름(서비스명)/요청 데이터 행 시작번호/요청 데이터 행 끝번호/출발역명/도착역명
            path_key = '646f7a76646a6f7733317842746455'
            path_api_url = 'http://swopenAPI.seoul.go.kr/api/subway/'+path_key+'/json/shortestRoute/0/10/'+searchword+'/'+destword
            path_response = requests.get(path_api_url)
            path_resdata = path_response.text
            path_obj = json.loads(path_resdata)
            try:
                path_obj = path_obj['shortestRouteList']
            except KeyError:
                print("keyerror")
                
            #최단 시간 찾기
            path_time = [9999,9999,9999,9999,9999,9999,9999,9999,9999,9999]
            
            i=0
            try:
                for time in path_obj:
                    path_time[i] = int(time.get('shtTravelTm'))
                    i=i+1
            except AttributeError:
                print("AttributeError")
            min_sht_path_time = min(path_time)
            for item in path_obj:
                sht_path_list = item.get('shtStatnNm')
                sht_path_msg = item.get('shtTravelMsg')
                sht_path_trans_cnt = item.get('shtTransferCnt')

                if min_sht_path_time == int(item.get('shtTravelTm')):
                    break
                
            sht_path_list = sht_path_list.replace(" ","")
            sht_path_list = sht_path_list.split(',')


            #path_value_0 = sht_path_list[0]
            print('\n\n')
            print(sht_path_list[0])
            print(sht_path_list[1])            
            print(sht_path_list[2])            
            
            #최소 환승 경로 찾기
            min_path_time = [9999,9999,9999,9999,9999,9999,9999,9999,9999,9999]
            min_trans_cnt = [10,10,10,10,10,10,10,10,10,10]
            i=0
            try:
                for item in path_obj:
                    if int(item.get('minTravelTm')) < 500: #쓰래기값 제거하기
                        min_path_time[i] = int(item.get('minTravelTm'))
                        min_trans_cnt[i] = int(item.get('minTransferCnt'))
                    i=i+1
            except AttributeError:
                print(AttributeError)
            print('\n\n\n리스트 테스트\n\n\n\n\n')
            print(min_path_time)
            print(min_trans_cnt)

            min_min_trans_cnt = min(min_trans_cnt) # 환승 횟수의 최솟값을 변수에 저장
            min_min_path_time = min(min_path_time) # 시간의 최솟값을 변수에 저장
            for item in path_obj:
                min_path_list = item.get('minStatnNm')
                min_path_msg = item.get('minTravelMsg')
                min_path_trans_cnt = item.get('minTransferCnt')
                if min_min_trans_cnt == int(item.get('minTransferCnt')) and min_min_path_time == int(item.get('minTravelTm')): # 환승 횟수가 최소면,
                    break
            
            min_path_list = min_path_list.replace(" ","")

            min_path_list = min_path_list.split(',')            
            
            
            print('dddddddd\n\n')
            print(min_path_list)
            print(min_path_trans_cnt)
            
            #shtTransferCnt <-- 환승 횟수 카운터
            #minTransferCnt

    
            
            
            #서울시 지하철역 정보 검색 (역명) https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do
            # 출발역 찾기
            api_url1 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+searchword
            response = requests.get(api_url1)
            resdata = response.text
            obj = json.loads(resdata)
            try:
                obj = obj['SearchInfoBySubwayNameService']
                obj = obj['row']
            except KeyError:
                print("keyerror")
                
                
            # 출발역 다음역 찾기 (호선 찾기 위함) (최단시간)
            sht_next_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+sht_path_list[1]
            sht_next_response = requests.get(sht_next_api_url)
            sht_next_resdata = sht_next_response.text
            sht_next_obj = json.loads(sht_next_resdata)
            try:
                sht_next_obj = sht_next_obj['SearchInfoBySubwayNameService']
                sht_next_obj = sht_next_obj['row']
            except KeyError:
                print("keyerror")
            
            # 출발역 다음역 찾기 (호선 찾기 위함) (최소환승)
            min_next_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+min_path_list[1]
            min_next_response = requests.get(min_next_api_url)
            min_next_resdata = min_next_response.text
            min_next_obj = json.loads(min_next_resdata)
            try:
                min_next_obj = min_next_obj['SearchInfoBySubwayNameService']
                min_next_obj = min_next_obj['row']
            except KeyError:
                print("keyerror")
                    
            # 도착역 찾기
            dest_api_url1 = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+destword
            dest_response = requests.get(dest_api_url1)
            dest_resdata = dest_response.text
            dest_obj = json.loads(dest_resdata)
            try:
                dest_obj = dest_obj['SearchInfoBySubwayNameService']
                dest_obj = dest_obj['row']
            except KeyError:
                print("keyerror")
                
            #출발 지점 호선 찾기
            print('호선찾기 테스트')
            line_list = []
            for item in obj:
                line_list += item.get('LINE_NUM')
                line_list += ','
            joined_line_list = " ".join(line_list)
            joined_line_list = joined_line_list.replace(" ","")
            joined_line_list = joined_line_list.split(',')
            joined_line_list = [v for v in joined_line_list if v]



            #출발 다음 지점 호선 찾기 (최단시간)
            next_line_list = []
            for item in sht_next_obj:
                next_line_list += item.get('LINE_NUM')
                next_line_list += ','
            joined_next_line_list = " ".join(next_line_list)
            joined_next_line_list = joined_next_line_list.replace(" ","")
            joined_next_line_list = joined_next_line_list.split(',')
            joined_next_line_list = [v for v in joined_next_line_list if v]
            
            #출발 다음 지점 호선 찾기 (최소환승)
            min_next_line_list = []
            for item in min_next_obj:
                min_next_line_list += item.get('LINE_NUM')
                min_next_line_list += ','
            min_joined_next_line_list = " ".join(min_next_line_list)
            min_joined_next_line_list = min_joined_next_line_list.replace(" ","")
            min_joined_next_line_list = min_joined_next_line_list.split(',')
            min_joined_next_line_list = [v for v in min_joined_next_line_list if v]
            
            #노선 찾기
            line = ''
            
            for item in joined_line_list:
                for jtem in joined_next_line_list:
                    if item == jtem:
                        line = jtem
                        break
            
            min_line = ''
            for item in joined_line_list:
                for jtem in min_joined_next_line_list:
                    if item == jtem:
                        min_line = jtem
                        break
            
            ### 출발 호선 기준으로 호선 내 지하철 역 찾기 (최단시간)
            #서울교통공사 노선별 지하철역 정보  http://data.seoul.go.kr/dataList/OA-15442/S/1/datasetView.do
            
            line_api_url = 'http://openapi.seoul.go.kr:8088/'+key_num+'/json/SearchSTNBySubwayLineInfo/1/200/ / /'+line
            line_response = requests.get(line_api_url)
            line_resdata = line_response.text
            line_obj = json.loads(line_resdata)
            
            print('testset')
            line_obj = line_obj['SearchSTNBySubwayLineInfo']
            line_obj = line_obj['row']
            station_list = []
            for item in line_obj:
                station_list += item.get('STATION_NM')
                station_list += ','
            joined_station_list = " ".join(station_list)
            joined_station_list = joined_station_list.replace(" ","")
            joined_station_list = joined_station_list.split(',')
            joined_station_list = [v for v in joined_station_list if v]
            
            print(joined_station_list)

            ### 출발 호선 기준으로 호선 내 지하철 역 찾기 (최소환승)
            #서울교통공사 노선별 지하철역 정보  http://data.seoul.go.kr/dataList/OA-15442/S/1/datasetView.do
            
            min_line_api_url = 'http://openapi.seoul.go.kr:8088/'+key_num+'/json/SearchSTNBySubwayLineInfo/1/200/ / /'+min_line
            min_line_response = requests.get(min_line_api_url)
            min_line_resdata = min_line_response.text
            min_line_obj = json.loads(min_line_resdata)
            
            print('testset')
            min_line_obj = min_line_obj['SearchSTNBySubwayLineInfo']
            min_line_obj = min_line_obj['row']
            min_station_list = []
            for item in min_line_obj:
                min_station_list += item.get('STATION_NM')
                min_station_list += ','
            min_joined_station_list = " ".join(min_station_list)
            min_joined_station_list = min_joined_station_list.replace(" ","")
            min_joined_station_list = min_joined_station_list.split(',')
            min_joined_station_list = [v for v in min_joined_station_list if v]
            
            print(min_joined_station_list)



            ####------------------------------------@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # 아래 코드 실행  (1회 환승을 한다면,)
            if sht_path_trans_cnt == '1':
                
                
                
                print('\n\n최단 시간 경로 - 환승을 1회 하는 경로입니다.')
                
                    
                #최소 시간 경로 환승경로 지정하기
                #sht_path_list
                print(sht_path_list)
                path_station_list = []
                for item in sht_path_list:
                    for jtem in joined_station_list:
                        if item == jtem:
                            path_station_list += jtem
                            path_station_list += ','
                            break
                        
                
                joined_path_station_list = " ".join(path_station_list)
                joined_path_station_list = joined_path_station_list.replace(" ","")
                joined_path_station_list = joined_path_station_list.split(',')
                
                print("이게 무슨경로인가여")        
                print(joined_path_station_list)
                # trans_station <--- 환승역임
                trans_station = joined_path_station_list[-2]
                print(trans_station)
                
                
                index = sht_path_list.index(trans_station)
                
                # 환승역 다음 역
                next_trans_station = sht_path_list[index+1]
                
                ####환승역 기준 다시 도착역 까지 경로
                #1회 환승 이후 노선 찾기
                
                #환승역 노선 찾기
                trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+trans_station
                trans_response = requests.get(trans_api_url)
                trans_resdata = trans_response.text
                trans_obj = json.loads(trans_resdata)
                try:
                    trans_obj = trans_obj['SearchInfoBySubwayNameService']
                    trans_obj = trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                trans_line_list = []
                for item in trans_obj:
                    trans_line_list += item.get('LINE_NUM')
                    trans_line_list += ','
                joined_trans_line_list = " ".join(trans_line_list)
                joined_trans_line_list = joined_trans_line_list.replace(" ","")
                joined_trans_line_list = joined_trans_line_list.split(',')
                joined_trans_line_list = [v for v in joined_trans_line_list if v]

                print(joined_trans_line_list)
                
                #환승역 다음역 노선 찾기
                next_trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+next_trans_station
                next_trans_response = requests.get(next_trans_api_url)
                next_trans_resdata = next_trans_response.text
                next_trans_obj = json.loads(next_trans_resdata)
                try:
                    next_trans_obj = next_trans_obj['SearchInfoBySubwayNameService']
                    next_trans_obj = next_trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                next_trans_line_list = []
                for item in next_trans_obj:
                    next_trans_line_list += item.get('LINE_NUM')
                    next_trans_line_list += ','
                next_joined_trans_line_list = " ".join(next_trans_line_list)
                next_joined_trans_line_list = next_joined_trans_line_list.replace(" ","")
                next_joined_trans_line_list = next_joined_trans_line_list.split(',')
                next_joined_trans_line_list = [v for v in next_joined_trans_line_list if v]

                print(next_joined_trans_line_list)
                
                #환승 이후 노선 찾기
                
                for item in joined_trans_line_list:
                    for jtem in next_joined_trans_line_list:
                        if item == jtem:
                            trans_line = jtem
                            break
                print(trans_line)
                
                #환승 이후 경로
                after_trans_path_list = sht_path_list[index:-1]

            elif sht_path_trans_cnt == '2':
                print('\n환승 횟수가 2회 입니다. 아래의 코드를 실행합니다.')
                                    
                #최소 시간 경로 환승경로 지정하기
                #sht_path_list
                print(sht_path_list)
                path_station_list = []
                for item in sht_path_list:
                    for jtem in joined_station_list:
                        if item == jtem:
                            path_station_list += jtem
                            path_station_list += ','
                            break
                        
                
                joined_path_station_list = " ".join(path_station_list)
                joined_path_station_list = joined_path_station_list.replace(" ","")
                joined_path_station_list = joined_path_station_list.split(',')
                
                print("이게 무슨경로인가여")        
                print(joined_path_station_list)
                # trans_station <--- 환승역임
                trans_station = joined_path_station_list[-2]
                print(trans_station)
                
                
                index = sht_path_list.index(trans_station)
                
                # 환승역 다음 역
                next_trans_station = sht_path_list[index+1]
                
                ####환승역 기준 다시 도착역 까지 경로
                #1회 환승 이후 노선 찾기
                
                #환승역 노선 찾기
                trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+trans_station
                trans_response = requests.get(trans_api_url)
                trans_resdata = trans_response.text
                trans_obj = json.loads(trans_resdata)
                try:
                    trans_obj = trans_obj['SearchInfoBySubwayNameService']
                    trans_obj = trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                trans_line_list = []
                for item in trans_obj:
                    trans_line_list += item.get('LINE_NUM')
                    trans_line_list += ','
                joined_trans_line_list = " ".join(trans_line_list)
                joined_trans_line_list = joined_trans_line_list.replace(" ","")
                joined_trans_line_list = joined_trans_line_list.split(',')
                joined_trans_line_list = [v for v in joined_trans_line_list if v]

                print(joined_trans_line_list)
                
                #환승역 다음역 노선 찾기
                next_trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+next_trans_station
                next_trans_response = requests.get(next_trans_api_url)
                next_trans_resdata = next_trans_response.text
                next_trans_obj = json.loads(next_trans_resdata)
                try:
                    next_trans_obj = next_trans_obj['SearchInfoBySubwayNameService']
                    next_trans_obj = next_trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                next_trans_line_list = []
                for item in next_trans_obj:
                    next_trans_line_list += item.get('LINE_NUM')
                    next_trans_line_list += ','
                next_joined_trans_line_list = " ".join(next_trans_line_list)
                next_joined_trans_line_list = next_joined_trans_line_list.replace(" ","")
                next_joined_trans_line_list = next_joined_trans_line_list.split(',')
                next_joined_trans_line_list = [v for v in next_joined_trans_line_list if v]

                print(next_joined_trans_line_list)
                
                #환승 이후 노선 찾기
                
                for item in joined_trans_line_list:
                    for jtem in next_joined_trans_line_list:
                        if item == jtem:
                            trans_line = jtem
                            break
                print(trans_line)
                
                #환승 이후 경로
                after_trans_path_list = sht_path_list[index:-1]

            else:
                print("환승 횟수가 0회이기 때문에, 환승 코드를 실행하지 않습니다.")
            
            ##############################################################
            if min_path_trans_cnt == '1':
                print('\n\n최소환승 경로 - 환승 횟수가 1회')
                #최소 환승 경로 환승경로 지정하기
                print('\n\n\n')
                print(min_path_list)
                min_path_station_list = []
                for item in min_path_list:
                    for jtem in min_joined_station_list:
                        if item == jtem:
                            min_path_station_list += jtem
                            min_path_station_list += ','
                            break
                        
                
                min_joined_path_station_list = " ".join(min_path_station_list)
                min_joined_path_station_list = min_joined_path_station_list.replace(" ","")
                min_joined_path_station_list = min_joined_path_station_list.split(',')
                
                print("이게 무슨경로인가여")        
                print(min_joined_path_station_list)
                # trans_station <--- 환승역임
                trans_station = min_joined_path_station_list[-2]
                print(trans_station)

                index = min_path_list.index(trans_station)
                
                # 환승역 다음 역
                next_trans_station = min_path_list[index+1]
                
                ####환승역 기준 다시 도착역 까지 경로
                #1회 환승 이후 노선 찾기
                
                #환승역 노선 찾기
                trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+trans_station
                trans_response = requests.get(trans_api_url)
                trans_resdata = trans_response.text
                trans_obj = json.loads(trans_resdata)
                try:
                    trans_obj = trans_obj['SearchInfoBySubwayNameService']
                    trans_obj = trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                trans_line_list = []
                for item in trans_obj:
                    trans_line_list += item.get('LINE_NUM')
                    trans_line_list += ','
                joined_trans_line_list = " ".join(trans_line_list)
                joined_trans_line_list = joined_trans_line_list.replace(" ","")
                joined_trans_line_list = joined_trans_line_list.split(',')
                joined_trans_line_list = [v for v in joined_trans_line_list if v]

                print(joined_trans_line_list)
                
                #환승역 다음역 노선 찾기
                next_trans_api_url = 'http://openAPI.seoul.go.kr:8088/'+key_num+'/json/SearchInfoBySubwayNameService/1/5/'+next_trans_station
                next_trans_response = requests.get(next_trans_api_url)
                next_trans_resdata = next_trans_response.text
                next_trans_obj = json.loads(next_trans_resdata)
                try:
                    next_trans_obj = next_trans_obj['SearchInfoBySubwayNameService']
                    next_trans_obj = next_trans_obj['row']
                except KeyError:
                    print("keyerror")
                
                next_trans_line_list = []
                for item in next_trans_obj:
                    next_trans_line_list += item.get('LINE_NUM')
                    next_trans_line_list += ','
                next_joined_trans_line_list = " ".join(next_trans_line_list)
                next_joined_trans_line_list = next_joined_trans_line_list.replace(" ","")
                next_joined_trans_line_list = next_joined_trans_line_list.split(',')
                next_joined_trans_line_list = [v for v in next_joined_trans_line_list if v]

                print(next_joined_trans_line_list)
                
                #환승 이후 노선 찾기
                
                for item in joined_trans_line_list:
                    for jtem in next_joined_trans_line_list:
                        if item == jtem:
                            min_trans_line = jtem
                            break
                print(min_trans_line)
                
                #환승 이후 경로
                min_after_trans_path_list = min_path_list[index:-1]

            elif min_path_trans_cnt == '2':
                print('최소환승 경로 환승 횟수가 2 회 ')
            else:
                print('환승 횟수 0 회 ')
                
            #서울교통공사_서울 도시철도 목적지 경로정보 https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15097640
            ''' -> API 오류 HTTP ERROR
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
            try:
                finobj = finobj["realtimeArrivalList"]
            except KeyError:
                print('keyerror_realtime')
            #############################################
            #try:
            return render(request,'detail.html',{'min_line':min_line,'min_trans_line':min_trans_line,'min_joined_path_station_list':min_joined_path_station_list,'min_after_trans_path_list':min_after_trans_path_list,'trans_line':trans_line,'after_trans_path_list':after_trans_path_list,'joined_path_station_list':joined_path_station_list,'line_obj':line_obj,'line':line,'trans_path_obj':trans_path_obj,'trans_path_list':trans_path_list,'min_min_path_time':min_min_path_time,'min_path_time':min_path_time,'obj' : obj,'min_path_list':min_path_list,'min_path_msg':min_path_msg,'sht_path_msg':sht_path_msg,'min_sht_path_time':min_sht_path_time,'path_time':path_time,'sht_path_list':sht_path_list,'path_obj':path_obj,'dest_obj':dest_obj , 'finobj' : finobj})
            #except UnboundLocalError:
                #print("UnboundLocalError")
    else:
        form = RouteForm()



    return render(request, 'home.html', {'form' : form})


def setting(request):
    return render(request, 'setting.html')


def detail(request):
    

    return render(request, 'detail.html')


def favorite(request):
    return render(request, 'favorite.html')