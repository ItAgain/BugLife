from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Operation
import datetime
import requests
import xmltodict
import json
import pandas as pd
import sklearn.model_selection
import sklearn.linear_model


class CardOperation(View):
    def get(self, request):
        all_operations = Operation.objects.all()
        all_json = {}
        for item in all_operations:
            all_json[item.id] = {
                'card_id': item.card_id,
                'amount': item.amount,
                'shop': item.shop,
                'date': item.date,
            }
        return JsonResponse(all_json)

    def post(self, request):
        json_body = json.loads(request.body)
        new_op = Operation.objects.create(
            card_id=json_body.get('card_id'),
            amount=json_body.get('amount'),
            shop=json_body.get('shop'),
            date=datetime.datetime.now()
        )
        return JsonResponse({'message': 'operation created'})


class SingleCardOperation(View):
    def patch(self, request, id):
        json_body = json.loads(request.body)
        op = Operation.objects.get(id=id)
        op.card_id = json_body['card_id']
        op.amount = json_body['amount']
        op.shop = json_body['shop']
        op.date = datetime.datetime.now()
        op.save()
        return JsonResponse({'message': f'operation {id} patched'})

    def delete(self, request, id):
        operation = Operation.objects.get(id=id)
        operation.delete()
        return JsonResponse({'message': f'operation {id} deleted'})


def index_view(request):
    date = '04/04/2024'
    resp = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}')
    resp_parsed = xmltodict.parse(resp.text)
    valutes = resp_parsed['ValCurs']['Valute']
    currencies = []
    for valute in valutes:
        if valute['CharCode'] == 'USD' or valute['CharCode'] == 'EUR' or valute['CharCode'] == 'GBP' or valute['CharCode'] == 'CHF':
            temp = valute['Value'].split(',')
            currencies.append([f'{temp[0]}.{temp[1]}', valute['Nominal'], valute['CharCode'], valute['Name']])

    start_date = '2023-01-01'
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
        dates.append(item['DT'][:10])
        rates.append(float(item['Rate']))

    dots = 1
    if len(dates) > 512:
        dots = (len(dates) // 512) + 1

    context = {
        'currencies': currencies,
        'dates': dates[::-dots],
        'rates': rates[::-dots],
    }

    return render(request, "index.html", context)


def key_rate_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if not start_date:
            start_date = '2020-01-01'
        if not end_date:
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
        dates.append(item['DT'][:10])
        rates.append(float(item['Rate']))

    dots = 1
    if len(dates) > 512:
        dots = (len(dates) // 512) + 1

    context = {
        'dates': dates[::-dots],
        'rates': rates[::-dots],
        'start_date': dates[-1],
        'end_date': dates[0]
    }
    return render(request, 'key_rate_page.html', context)


def metals_rate_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        metal = request.POST.get('cod_met')
        if not start_date:
            start_date = '2020-01-01'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if not metal:
            metal = '1'
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
        'metal_name': metal_name,
        'start_date': start_date,
        'end_date': dates[-1]
    }
    return render(request, 'metals_rate_page.html', context)


def currency_rate_view(request):
    if request.method == 'POST':
        start_date_list = request.POST.get('start_date').split('-')
        end_date_list = request.POST.get('end_date').split('-')
        start_date = f'{start_date_list[2]}/{start_date_list[1]}/{start_date_list[0]}'
        end_date = f'{end_date_list[2]}/{end_date_list[1]}/{end_date_list[0]}'
        currency = request.POST.get('currency')
        if not start_date:
            start_date = '01/01/2020'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%d/%m/%Y')
        if not currency:
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

    currency_name = 'null'
    if currency == 'R01235':
        currency_name = 'Доллар США'
    elif currency == 'R01239':
        currency_name = 'Евро'

    start_date_list = dates[0].split('.')
    end_date_list = dates[-1].split('.')

    context = {
        'dates': dates[::dots],
        'rates': rates[::dots],
        'currency_name': currency_name,
        'start_date': f'{start_date_list[2]}-{start_date_list[1]}-{start_date_list[0]}',
        'end_date': f'{end_date_list[2]}-{end_date_list[1]}-{end_date_list[0]}',
    }
    return render(request, 'currency_rate_page.html', context)


def predict_view(request):
    df = pd.read_csv('static/housing.csv')
    df.set_index("id")
    x = df.drop(["price"], axis=1)   # убираем из датафрейма колонку цены
    y = df["price"]
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y)
    model = sklearn.linear_model.LinearRegression()
    model.fit(x_train, y_train)
    model.score(x_test, y_test)
    #data = [[1808, 10, 0, 0, 93943, 10, 3, 0, 0, 0, 0, 0, 31]]
    test_result = ''
    predict = 0
    credit_summ = 0
    area = 0,
    bedrooms = 0
    bathrooms = 0
    stories = 0
    stories_1 = 1
    guestroom = 0
    basement = 0
    hotwaterheating = 0
    airconditioning = 0
    parking = 0
    prefarea= 0
    furnishingstatus = 0
    if request.method == 'POST':
        # price = request.POST.get('price')
        area = request.POST.get('area')
        if not area:
            area = 0
        bedrooms = request.POST.get('bedrooms')
        if not bedrooms:
            bedrooms = 0
        bathrooms = request.POST.get('bathrooms')
        if not bathrooms:
            bathrooms = 0
        stories = request.POST.get('stories')
        if not stories:
            stories = 0
        stories_1 = 1
        guestroom = request.POST.get('guestroom')
        if not guestroom:
            guestroom = 0
        basement = request.POST.get('basement')
        if not basement:
            basement = 0
        hotwaterheating = request.POST.get('hotwaterheating')
        if not hotwaterheating:
            hotwaterheating = 0
        airconditioning = request.POST.get('airconditioning')
        if not airconditioning:
            airconditioning = 0
        parking = request.POST.get('parking')
        if not parking:
            parking = 0
        prefarea = request.POST.get('prefarea')
        if not prefarea:
            prefarea = 0
        furnishingstatus = request.POST.get('furnishingstatus')
        if not furnishingstatus:
            furnishingstatus = 0

        credit_summ = request.POST.get('credit_summ')
        if not credit_summ:
            credit_summ = 0

        data = [[0, area, bedrooms, bathrooms, stories, stories_1, guestroom, basement, hotwaterheating,
                 airconditioning, parking, prefarea, furnishingstatus]]

        my_test = pd.DataFrame(data, columns=[
            'id', 'area', 'bedrooms', 'bathrooms', 'stories', 'stories.1',
            'guestroom', 'basement', 'hotwaterheating', 'airconditioning',
            'parking', 'prefarea', 'furnishingstatus'])
        predict = model.predict(my_test)
        if int(credit_summ) > predict:
            test_result = 'Ипотечный кредит одобрен'
        else:
            test_result = 'Ипотечный кредит отклонен'

    context = {
        'test_result': test_result,
        'cur_data': {
            "area": area,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "stories": stories,
            "guestroom": guestroom,
            "basement": basement,
            "hotwaterheating": hotwaterheating,
            "airconditioning": airconditioning,
            "parking": parking,
            "prefarea": prefarea,
            "furnishingstatus": furnishingstatus,
            "credit_summ": credit_summ,
            "price": predict
        }
    }
    return render(request, 'mortgage_predict_page.html', context)