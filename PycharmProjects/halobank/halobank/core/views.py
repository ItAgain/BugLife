import xmltodict
from django.shortcuts import render
import datetime
import requests


def index_view(request):
    return render(request, 'index.html')


def key_rate_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date_date')
        if start_date == '':
            start_date = '2020-01-01'
        if end_date == '':
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        start_date = '2020-01-01'
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    url = "http://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    data = f'''<?xml version=\"1.0\" encoding=\"utf-8\"?>\n
        <soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n
        <soap12:Body>\n
            <KeyRate xmlns=\"http://web.cbr.ru/\">\n
                <fromDate>{start_date}</fromDate>\n
                <ToDate>{end_date}</ToDate>\n
            </KeyRate>\n
        </soap12:Body>\n
        </soap12:Envelope>'''
    headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
    response = requests.request("POST", url, headers=headers, data=data)
    resp_dict = xmltodict.parse(response.text)
    key_rate = resp_dict['soap:Envelope']['soap:Body']['KeyRateResponse']['KeyRateResult']['diffgr:diffgram']['KeyRate']['KR']

    dates, rates = [], []
    for item in key_rate:
        dates.append(item['DT'])
        rates.append(float(item['Rate']))

    dots = 1
    if len(dates) > 512:
        dots = (len(dates) // 512) + 1

    context = {
        'dates': dates[::-dots],
        'rates': rates[::dots],
    }
    return render(request, 'key_rate_page.html', context)


def metals_rate_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        metal = request.POST.get('cod_met')
        if start_date == '':
            start_date = '2020-01-01'
        if end_date == '':
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        start_date = '2020-01-01'
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        metal = '1'

    url = "http://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    data = f'''<?xml version=\"1.0\" encoding=\"utf-8\"?>\n
                <soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n
                <soap12:Body>\n
                    <DragMetDynamic xmlns=\"http://web.cbr.ru/\">\n 
                        <fromDate>{start_date}</fromDate>\n      
                        <ToDate>{end_date}</ToDate>\n    
                    </DragMetDynamic>\n
                </soap12:Body>\n
                </soap12:Envelope>'''
    headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
    response = requests.request("POST", url, headers=headers, data=data)
    resp_dict = xmltodict.parse(response.text)
    drag_met = resp_dict['soap:Envelope']['soap:Body']['DragMetDynamicResponse']['DragMetDynamicResult']['diffgr:diffgram']['DragMetall']['DrgMet']

    dates, rates = [], []
    for item in drag_met:
        if item['CodMet'] == metal:
            dates.append(item['DateMet'][:10])
            rates.append(float(item['price']))

    dots = 1
    if len(dates) > 512:
        dots = (len(dates) // 512) + 1

    metal_name = 'null'
    if metal == '1':
        metal_name = 'Золото'
    elif metal == '2':
        metal_name = 'Серебро'
    elif metal == '3':
        metal_name = 'Платина'

    context = {
        'dates': dates[::dots],
        'rates': rates[::dots],
        'metal_name': metal_name
    }
    return render(request, 'metals_rate_page.html', context)


def currency_rate_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        currency = request.POST.get('currency')
        if start_date == '':
            start_date = '01/01/2020'
        if end_date == '':
            end_date = datetime.datetime.now().strftime('%d/%m/%Y')
        if currency == '':
            currency = 'R01235'
    else:
        start_date = '01/01/2020'
        end_date = datetime.datetime.now().strftime('%d/%m/%Y')
        currency = 'R01235'

    url = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start_date}&date_req2={end_date}&VAL_NM_RQ={currency}"
    response = requests.request("POST", url, )
    resp_dict = xmltodict.parse(response.text)
    records = resp_dict['ValCurs']['Record']

    dates, rates = [], []
    for item in records:
        dates.append(item['@Date'])
        rates.append(float(item['VunitRate'].replace(',', '.')))

    dots = 1
    if len(dates) > 512:
        dots = (len(dates) // 512) + 1

    context = {
        'dates': dates[::dots],
        'rates': rates[::dots],
    }
    return render(request, 'currency_rate_page.html', context)
