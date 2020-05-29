from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth.models import User

from django.contrib import messages

from .models import Category, Brand, Item, Product, Record, Bill, Order

import itertools  
from decimal import Decimal



# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, "inventory/login.html")
    else:
        return HttpResponseRedirect(reverse('dashboard'))


def login_view(request):
    if request.method == 'GET':
        return render(request, "inventory/login.html")     
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "inventory/login.html", {"messages": "Invalid username and/or password. Please try again."} )


def register(request):
    if request.method == 'GET':
        return render(request, "inventory/register.html")
    if request.method == 'POST': 
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']        
        username = request.POST['username']        
        password = request.POST['password']

        try:
            user = User.objects.create_user(username, None, password)
        except IntegrityError:
            return render(request, "inventory/register.html", {"messages": "Account exisits. Please try another one."})
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        return render(request, "inventory/register.html", {"messages": "Account has been created. Please login to your account."})

def logout_view(request):
    logout(request)
    return render(request, "inventory/login.html", {"messages": "You are successfully logout."})

def dashboard(request):
    if request.method == "GET":
        context = {
            "product": Product.objects.last(),
            "bill": Bill.objects.last(),
            "order": Order.objects.last(),
        }
        return render(request, "inventory/dashboard.html", context)

def product(request):
    context = {
        "categorys": Category.objects.all(),
        "brands": Brand.objects.all(),
        "items": Item.objects.all()
    }
    return render(request, "inventory/product.html", context)

def searchProduct(request):
    if request.method == 'POST':
        term = request.POST['searchby']
        detail = request.POST['search']
        print(term, detail)
        if term == 'Category':
            res = Product.objects.filter(category__name__icontains=detail)
            if res:
                print(res)
                context = {
                    "categorys": Category.objects.all(),
                    "brands": Brand.objects.all(),
                    "items": Item.objects.all(),
                    "products": res
                }  
                return render(request, "inventory/product.html", context)
            else:
                messages.error(request, "No Product Found Under This Category")
                return HttpResponseRedirect(reverse('product'))
      
        elif term == 'Brand':   
            res = Product.objects.filter(brand__name__icontains=detail)
            if res:
                print(res)
                context = {
                    "categorys": Category.objects.all(),
                    "brands": Brand.objects.all(),
                    "items": Item.objects.all(),
                    "products": res
                }  
                return render(request, "inventory/product.html", context)
            else:
                messages.error(request, "No Product Found Under This Category")
                return HttpResponseRedirect(reverse('product'))
            
        elif term == 'Item':
            res = Product.objects.filter(item__name__icontains=detail)
            if res:
                print(res)
                context = {
                    "categorys": Category.objects.all(),
                    "brands": Brand.objects.all(),
                    "items": Item.objects.all(),
                    "products": res
                }  
                return render(request, "inventory/product.html", context)
            else:
                messages.error(request, "No Product Found Under This Category")
                return HttpResponseRedirect(reverse('product'))

 
def addProduct(request):
    if request.method == 'POST':
        category = request.POST['category']
        brand = request.POST['brand']
        item = request.POST['item']

        try:
            c = Category.objects.get(name=category)
            b = Brand.objects.get(name=brand)
            i = Item.objects.get(name=item)
        except ObjectDoesNotExist:
            messages.error(request, "Invalid Entries.")
            return HttpResponseRedirect(reverse('product'))

        try:
            p = Product.objects.get(category=c, brand=b, item=i)        
        except ObjectDoesNotExist:
            p = Product(category=c, brand=b, item=i)
            p.save()  
            messages.success(request, "New Product Added.")
            return HttpResponseRedirect(reverse('product'))
        messages.error(request, "Product Already Exisits.")
        return HttpResponseRedirect(reverse('product'))


def bill(request):
    if request.method == "GET":
        context = {
            "products": Product.objects.all(),
        }
        return render(request, "inventory/bill.html", context)

def addBill(request):
    if request.method == 'POST':
        rate = request.POST.getlist("rate")
        pid = request.POST.getlist("enter_bill")
        quan = request.POST.getlist("quan")
        tot = request.POST.getlist("total")

        date = request.POST['date']
        inv = request.POST['invoice']
        cpy = request.POST['company']
        ref = request.POST['ref']
        print(date, inv, cpy, ref)

        # Create BILL info
        bill = Bill.objects.filter(invoice=inv)  
        if bill:
            messages.error(request, "Duplicate Bill Number")
            return HttpResponseRedirect(reverse('bill'))
        else: 
            bill = Bill(invoice=inv, date=date, company=cpy, reference=ref)
            bill.save()

        # Update PRODUCT quantity
        for (prid, q) in zip(pid, quan):
            prod = Product.objects.get(id=prid)
            prod.quantity = prod.quantity + int(q)
            prod.save()
        
        # Create RECORD and add them to BILL
        for (p, r, q, t) in zip(pid, rate, quan, tot):
            pname = Product.objects.get(id=p)
            print(pname, r, int(q), t)
            record = Record(name=pname, rate=r, quantity=int(q), total=t, product=pname)
            record.save()
            bill.records.add(record)
            bill.save()

        messages.success(request, "New Bill Added.")
        return HttpResponseRedirect(reverse('bill'))
 
def searchBill(request):
    if request.method == 'POST':
        term = request.POST['searchby']
        detail = request.POST['search']
        print(term, detail)

        if term == 'Date':
            bills = Bill.objects.filter(date__icontains=detail)
            if bills:
                context = {
                    "bills": bills,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/bill.html", context)
            else:
                messages.error(request, "No Bill Found Under This Date")
                return HttpResponseRedirect(reverse('bill'))
        
        elif term == 'Bill':
            bills = Bill.objects.filter(invoice__icontains=detail)
            if bills:
                context = {
                    "bills": bills,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/bill.html", context)
            else:
                messages.error(request, "No Bill Found Under This Bill Number.")
                return HttpResponseRedirect(reverse('bill'))
        
        elif term == 'Company':
            bills = Bill.objects.filter(company__icontains=detail)
            if bills:
                context = {
                    "bills": bills,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/bill.html", context)
            else:
                messages.error(request, "No Bill Found Under This Company.")
                return HttpResponseRedirect(reverse('bill'))

def bill_detail(request, bill_num):
    if request.method == 'GET':
        try:
            bill = Bill.objects.get(invoice=bill_num)
        except ObjectDoesNotExist:
            messages.error(request, "Error Occurs. Please Try Again.")
            return HttpResponseRedirect(reverse('bill'))
        
        records = bill.records.all()
        if records:
            context = {
                "bill" : bill,
                "records" : records,
            }
            return render(request, "inventory/billDetail.html", context)
        else:
            messages.error(request, "No Records Under This Bill")
            return HttpResponseRedirect(reverse('bill'))

def bill_update(request, bill_num):
    if request.method == 'POST':
        rate = request.POST.getlist("rate")
        quan = request.POST.getlist("quan")
        tot = request.POST.getlist("total")
        print(rate, quan, tot)

        date = request.POST['date']
        cpy = request.POST['company']
        ref = request.POST['ref']
        print(date, cpy, ref)
        
        # get bill detail
        bill = Bill.objects.get(invoice=bill_num)

        # update bill attributes
        if bill.date != date:
            bill.date = date
            bill.save()
        if bill.company != cpy:
            bill.company = cpy
            bill.save()
        if bill.reference != ref:
            bill.reference = ref
            bill.save()

        # update bill's product detail
        records = bill.records.all()
        for (rec, r, q, t) in zip(records, rate, quan, tot):
            if rec.rate != Decimal(r):
                rec.rate = Decimal(r)
            if rec.quantity != int(q):
                p = rec.product
                dif = int(q) - int(rec.quantity)
                print(dif)
                p.quantity = p.quantity + dif
                print(f"current product quantity {p.quantity}")
                rec.quantity = q
                p.save()
            if rec.total != Decimal(t):
                rec.total = Decimal(t)
            rec.save()
            
    messages.success(request, "Bill Updated and Saved.")
    return HttpResponseRedirect(reverse('bill_detail', kwargs={'bill_num':bill_num})) 


def bill_delete(request, bill_num):
    if request.method == "POST":
        try:
            bill = Bill.objects.get(invoice=bill_num)
        except ObjectDoesNotExist:
            messages.error(request, "Error Occurs - Delete Failed. Please Try Again")
            return HttpResponseRedirect(reverse('bill_detail', kwargs={'bill_num':bill_num}))
        records = bill.records.all()
        for rec in records:
            p = rec.product
            p.quantity = p.quantity - rec.quantity
            print(p.quantity)
            p.save()
            rec.delete()
        bill.delete()
        messages.success(request, "Bill Successfully Deleted.")
        return HttpResponseRedirect(reverse('bill'))

def order(request):
    if request.method == 'GET':
        context = {
            "products": Product.objects.all(),
        }
        return render(request, "inventory/order.html", context)

def addOrder(request):
    if request.method == 'POST':
        rate = request.POST.getlist("rate")
        pid = request.POST.getlist("enter_order")
        quan = request.POST.getlist("quan")
        tot = request.POST.getlist("total")

        date = request.POST['date']
        inv = request.POST['invoice']
        cus = request.POST['customer']
        ref = request.POST['ref']
        print(date, inv, cus, ref)

        order = Order.objects.filter(invoice=inv)  
        if order:
            messages.error(request, "Duplicate Order Number")
            return HttpResponseRedirect(reverse('order'))
        else: 
            # check inventory stock first
            # for (prid, q) in zip(pid, quan):
            #     prod = Product.objects.get(id=prid)
            #     if (prod.quantity < int(q)):
            #         messages.error(request, f"There is No Enough Quantity For {prod} To Deduct.")
            #         return HttpResponseRedirect(reverse('order'))

            # Create New Order         
            new_order = Order(invoice=inv, date=date, customer=cus, reference=ref) 
            new_order.save()

            for (prid, q) in zip(pid, quan):
                prod = Product.objects.get(id=prid)
                prod.quantity = prod.quantity - int(q)
                prod.save()
                print(prod.quantity)

            for (p, r, q, t) in zip(pid, rate, quan, tot):
                pname = Product.objects.get(id=p)
                print(pname, r, int(q), t)
                record = Record(name=pname, rate=r, quantity=int(q), total=t, product=pname)
                record.save()
                new_order.records.add(record)
                new_order.save()
            
            messages.success(request, "New Order Added.")
            return HttpResponseRedirect(reverse('order'))    


def searchOrder(request):
    if request.method == 'POST':
        term = request.POST['searchby']
        detail = request.POST['search']
        print(term, detail)

        if term == 'Date':
            orders = Order.objects.filter(date__icontains=detail)
            if orders:
                context = {
                    "orders": orders,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/order.html", context)
            else:
                messages.error(request, "No Order Found Under This Date")
                return HttpResponseRedirect(reverse('order'))
        
        elif term == 'Order':
            orders = Order.objects.filter(invoice__icontains=detail)
            if orders:
                context = {
                    "orders": orders,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/order.html", context)
            else:
                messages.error(request, "No Order Found Under This Order Number.")
                return HttpResponseRedirect(reverse('order'))
        
        elif term == 'Customer':
            orders = Order.objects.filter(customer__icontains=detail)
            if orders:
                context = {
                    "orders": orders,
                    "products": Product.objects.all(),
                }
                return render(request, "inventory/order.html", context)
            else:
                messages.error(request, "No Order Found Under This Customer.")
                return HttpResponseRedirect(reverse('order'))

def order_detail(request, order_num):
    if request.method == 'GET':
        try:
            order = Order.objects.get(invoice=order_num)
        except ObjectDoesNotExist:
            messages.error(request, "Error Occurs. Please Try Again.")
            return HttpResponseRedirect(reverse('order'))
        
        records = order.records.all()
        if records:
            context = {
                "order" : order,
                "records" : records,
            }
            return render(request, "inventory/orderDetail.html", context)
        else:
            messages.error(request, "No Records Under This Order")
            return HttpResponseRedirect(reverse('order'))

def order_update(request, order_num):
    if request.method == 'POST':
        rate = request.POST.getlist("rate")
        quan = request.POST.getlist("quan")
        tot = request.POST.getlist("total")
        print(rate, quan, tot)

        date = request.POST['date']
        cus = request.POST['customer']
        ref = request.POST['ref']
        print(date, cus, ref)
        
        # get bill detail
        order = Order.objects.get(invoice=order_num)

        # update bill attributes
        if order.date != date:
            order.date = date
            order.save()
        if order.customer != cus:
            order.customer = cus
            order.save()
        if order.reference != ref:
            order.reference = ref
            order.save()

        # update bill's product detail
        records = order.records.all()
        for (rec, r, q, t) in zip(records, rate, quan, tot):
            if rec.rate != Decimal(r):
                rec.rate = Decimal(r)
            if rec.quantity != int(q):
                p = rec.product
                p.quantity = p.quantity + rec.quantity - int(q)
                print(f"current product quantity {p.quantity}")
                rec.quantity = int(q)
                p.save()
            if rec.total != Decimal(t):
                rec.total = Decimal(t)
            rec.save()
            
    messages.success(request, "Order Updated and Saved.")
    return HttpResponseRedirect(reverse('order_detail', kwargs={'order_num':order_num})) 


def order_delete(request, order_num):
    if request.method == "POST":
        try:
            order = Order.objects.get(invoice=order_num)
        except ObjectDoesNotExist:
            messages.error(request, "Error Occurs - Delete Failed. Please Try Again")
            return HttpResponseRedirect(reverse('order_detail', kwargs={'order_num':order_num}))
        records = order.records.all()
        for rec in records:
            p = rec.product
            p.quantity = p.quantity + rec.quantity
            print(p.quantity)
            p.save()
            rec.delete()
        order.delete()
        messages.success(request, "Order Successfully Deleted.")
        return HttpResponseRedirect(reverse('order'))