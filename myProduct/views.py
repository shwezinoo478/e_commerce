from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import *
from django.views.generic import ListView
from django.core.paginator import Paginator
from .forms import NewUserForm
from django.contrib.auth import login , authenticate ,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.

def get_category( request ):
    categorys = Category.objects.all().order_by('name')
    cat_list={}
    for cate in categorys:
        cat_list[cate.name] = cate.pk
    return JsonResponse(cat_list)


class product_item( ListView):
    def get( self, request ):
        category_id_active = 'all'
        if'category' in request.GET:
            category_id_active = request.GET['category']
            products = Product.objects.all().filter(cate_id = request.GET['category'])
        elif 'q' in request.GET:
            print ( request.GET['q'])
            products = Product.objects.all().filter(name__contains = request.GET['q']) | Product.objects.all().filter(description__contains = request.GET['q'])
             
        elif 'discount' in request.GET:
            products = Product.objects.all().filter(discount__gte = 1)
        else:
            products = Product.objects.all() 
        paginator = Paginator(products , 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        
        return render( request, 'view_product.html' , 
        {"products" : page_obj , 'count':products.count() , 'category_id_active':category_id_active } 
        )

def get_details( request , id : int):
    is_authenticated = request.user.is_authenticated
    if(is_authenticated):
        product_details = Product.objects.get(pk = id)
        return render( request , 'view_detail.html' ,
            {"product_details" : product_details})
            
    else:
        return redirect("login")
        
        
@csrf_exempt
def register_request( request):
    if request.method == "POST":
	    form = NewUserForm(request.POST)
	    if form.is_valid():
		    user = form.save()
		    login(request, user)
		    messages.success(request, "Registration successful." )
		    return redirect("login")
	    messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render ( request,"myProduct/register_home.html" , {"register_form":form})

@csrf_exempt
def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home_view")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="myProduct/login_home.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home_view")
    
def cache_store(request , id:int , qty:int):
    product_key = id
    product_result = cache.get(id)
    if product_result is None:
        product = Product.objects.get(pk = id)
        price = product.price
        print(price)
        product_list = {}
        print ("This is from db")
        cache.set(id , product)
    else:
        print("This is from cache")
        product = cache.get(id)

def cache_recipes_view(request , id : int ):
    product_key = id
    data = request.POST
    qty = data.get("qtyLabel")

    print(type(qty))
    qty = int(qty)

    product = Product.objects.get(pk = id)
    print("discount is " +str(product.discount))
    name = product.name
    image = product.product_img
    if(product.discount == 0):
            
        price=product.price
    else:
        price = product.Discount_price
        
    print(qty)
    product_result = cache.get(id)
    if product_result is None:
        total = qty * price
        print(price)
        product_list = {"id":id,"image":image,"name":name,"price":price,"qty":qty ,"total":total}
        print ("This is from db")
        
    else:
        print("This is from cache")
        product = cache.get(id)
        qty_update =product["qty"]+ qty
        total_update = qty_update*price
        print(product["qty"])
        product_list = {"id":id,"image":image,"name":name,"price":price,"qty":qty_update ,"total":total_update}
    cache.set(id , product_list , timeout=3600)
    count = 0
    for index,value in (cache.get(id)).items():
        count = count+1
    return redirect("home_view")

def cart_list_view(request):
    is_authenticated = request.user.is_authenticated
    count = 0
    if(is_authenticated):
        cache_test_keys = cache._cache.get_client(1).keys()
        print(f"{type(cache_test_keys)}")
        print(f"This is just test =>>> {cache_test_keys}")
        cache_keys = cache._cache.get_client().keys()
        list_cache_store = []
        total_cash = 0
        for k in cache_keys:
            key= (k.decode("utf-8"))[3:]
            print(key)
            product = cache.get(key)
            print(f"Price is {product['total']} ")
            total_cash = total_cash + product['total']
            list_cache_store.append(product)
            
            for index,value in (cache.get(key)).items():
                count = count+1

        print(f"Total cash is {total_cash}")
    else:
        print("login in againg")
        return redirect("login")

    return render(request ,"cacheData/cardProduct.html" ,{"list_cache":list_cache_store ,'total':total_cash , 'countCacheItem':count} )
##cache.clear()

def del_key(request, id:str):
    cache.delete(id)
    return redirect("cartData")

def order_item(request):
    return render(request, 'customerInfo/customerInfo.html')

def customerInsertData(request):
    order_list = []
    name= request.POST.get("name")
    email= request.POST.get("email")
    phone= request.POST.get("phone")
    region= request.POST.get("region")
    city= request.POST.get("city")
    street= request.POST.get("street_no")
    address = f"{region} {city} ({street})"
    print(phone)
    print("city is "+str(city))
    print("region is "+str(region))
    print("street is "+str(street))

    print(address)
    customer_test = Customer.objects.all().filter(name = name)
    new_customer = True
    for customer in customer_test:
        if(customer.name == name and customer.email == email and customer.phone == phone and customer.address == address):
            print("Same people")
            id_data = customer.id
            new_customer = False
            customer_data = customer
    if(new_customer == True):
        customer = Customer(name=name,email=email,phone=phone,address=address)
        customer.save()
        id_data = customer.id
        customer_data = customer
    print(customer_test)
    cache_keys = cache._cache.get_client().keys()
    print(f"Cache keys are {cache_keys}")
    total_cash = 0
    for k in cache_keys:
        key= (k.decode("utf-8"))[3:]
        print(key)
        product = cache.get(key)
        print(f"Price is {product['total']} ")
        total_cash = total_cash + product['total']


        id_product = product["id"]
        price = product["price"]
        qty = product["qty"]
        product= Product.objects.get(pk = id_product )
        customer = Customer.objects.get(pk = id_data)


        order = Order(price = price , qty = qty , customer_id = customer ,product_id = product)
        order.save()
        order_list.append(order)
        print(f"{order.id} is saved ???")
        for index,value in (cache.get(key)).items():
            print(f"{index} is {value}")
    

    return render(request, 'customerInfo/bouncherInfo.html' ,{"customer":customer_data , "order_list":order_list ,"total":total_cash})

def clear_cache(request):
    cache.clear()
    return redirect("home_view")