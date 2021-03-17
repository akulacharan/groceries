from django.shortcuts import render
from django.http import HttpResponse
from math import *
import json
from . models import Product,Contact,Orders,OrderUpdate,Offers
from django.views.decorators.csrf import csrf_exempt
from . PatTm import Checksum
# Create your views here.

MERCHANTKEY = 'HGTDcRZU1NPosiv7';


def index(request):
    offers=Offers.objects.all()
    # products = Product.objects.all()
    # print(products)
    # n = len(products)
    # nslides = n//4 + ceil((n/4)-(n//4))
    # params = {'no_of_slides': nslides,'range':range(1,nslides),'product':products}
    # allprods = [[products,range(1,nslides),nslides],[products,range(1,nslides),nslides]]
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    # print(cats)
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nslides), nslides])
    params = {'allprods': allprods,'offers':offers}
    return render(request, 'home.html',params)

def about(request):
    return render(request,'about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        desc = request.POST['desc']
        print(name,email,phone,desc)
        Contact.objects.create(name=name,email=email,phone=phone,desc=desc)
        thanks = True
        return render(request, 'contact.html', {'thanks': thanks})

    return render(request,'contact.html')

def tracker(request):
    if request.method == "POST":
        OrderId = request.POST['OrderId']
        email = request.POST['email']
        try:
            order = Orders.objects.filter(order_id = OrderId,email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id = OrderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson":order[0].items_json},default=str)
                    print(response)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"Noitem"}')
        except Exception as e:

            return HttpResponse('{"status":"error"}')

    return render(request,'track.html')




def searchMatch(query,item):
    '''Return only true when if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    # print(cats)
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]

        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nslides), nslides])

    params = {'allprods': allprods,'msg':""}
    if len(allprods) == 0 or len(query) < 4:
        params = {"msg":"Please enter the relavent details of your reqierd item."}
    return render(request, 'search.html', params)




def prodView(request,myid):
    product = Product.objects.filter(id=myid)
    print(product)
    return render(request,'prodview.html',{'product':product[0]})

def cancelorder(request):
    if request.method == "POST":
        mobile = request.POST['mobile']
        email = request.POST['email']
        #print(mobile,email)

        order = Orders.objects.filter(mobile=mobile)
        order_update = OrderUpdate.objects.filter(email=email)

        order_count = Orders.objects.filter(mobile=mobile).count()
        order_update_count = OrderUpdate.objects.filter(email=email).count()

        #print(order_count, order_update_count)

        if order_count >0 and order_update_count >0 :
            order.delete()
            order_update.delete()

            thanks = True

            return render(request, 'cancelorder.html', {'thanks': thanks})
        else:

            return HttpResponse("<script>alert('NO orders found!!')</script>")

    return render(request,'cancelorder.html')




def checkout(request):
    if request.method == "POST":
        name = request.POST['name']
        amount = request.POST['amount']
        items_json = request.POST['itemsJson']
        email = request.POST['email']
        address = request.POST['address1'] + "----" + request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip_code']
        mobile = request.POST['mobile']
        order = Orders(name=name,amount=amount,email=email,address=address,city=city,state=state,zip_code=zip_code,mobile=mobile,items_json=items_json)
        order.save()
        update = OrderUpdate(email=email,order_id = order.order_id,update_desc = 'The order has been placed')
        update.save()
        thank = True
        id = order.order_id
        #return render(request,'checkout.html',{'thank':thank,'id':id})
        # Request paytm to transfer the amount to your account after payment by User
        param_dict ={

            'MID':'cxEEpW98470775849731',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANTKEY)
        '''Use merchant-id(MID) and key provided to you by PayTm in your real business website'''
        return render(request,'paytm.html',{'param_dict':param_dict})


    return render(request,'checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict,MERCHANTKEY,checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order successfull')
        else:
            print('Order was not successfull because'+ response_dict['RESPMSG'])
    return render(request,'paymentstatus.html',{'response':response_dict})



