from .models import stock
from django.db.models import F
import datetime
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
# from reportlab.pdfgen import canvas
from .models import Customer, Comment, Order, stock, Food, RawItem, Data, Cart, OrderContent, Staff, DeliveryBoy, FoodCategories
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['firstname']
            user.last_name = form.cleaned_data['lastname']
            user.email = form.cleaned_data['email']
            user.username = user.email.split('@')[0]
            user.set_password(form.cleaned_data['password'])
            user.save()
            address = form.cleaned_data['address']
            contact = form.cleaned_data['contact']
            customer = Customer.objects.create(
                customer=user, address=address, contact=contact)
            customer.save()
            return redirect('/accounts/login/')

    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
@staff_member_required
def dashboard_admin(request):
    comments = Comment.objects.count()
    orders = Order.objects.count()
    customers = Customer.objects.count()
    completed_orders = Order.objects.filter(payment_status="Completed")
    top_customers = Customer.objects.filter().order_by('-total_sale')
    latest_orders = Order.objects.filter().order_by('-order_timestamp')
    datas = Data.objects.filter().order_by('date')
    sales = 0
    today_min = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(
        datetime.date.today(), datetime.time.max)
    today_orders = Order.objects.filter(
        order_timestamp__range=(today_min, today_max)).count()

    today_amount = sum(Order.objects.filter(order_timestamp__range=(
        today_min, today_max)).filter().values_list('total_amount', flat=True))

    date = datetime.date.today()
    start_week = date - datetime.timedelta(date.weekday())
    start_month = datetime.date.today().replace(day=1)
    start_year = datetime.date.today().replace(month=1, day=1)

    week_min = datetime.datetime.combine(
        start_week, datetime.time.min)
    week = Order.objects.filter(
        order_timestamp__range=(week_min, today_max)).count()
    week_amount = sum(Order.objects.filter(order_timestamp__range=(
        week_min, today_max)).filter().values_list('total_amount', flat=True))
    month = Order.objects.filter(
        order_timestamp__range=(start_month, today_max)).count()
    month_amount = sum(Order.objects.filter(order_timestamp__range=(
        start_month, today_max)).filter().values_list('total_amount', flat=True))
    year = Order.objects.filter(
        order_timestamp__range=(start_year, today_max)).count()
    year_amount = sum(Order.objects.filter(order_timestamp__range=(
        start_year, today_max)).filter().values_list('total_amount', flat=True))

    for order in completed_orders:
        sales += order.total_amount

    context = {
        'comments': comments,
        'orders': orders,
        'customers': customers,
        'sales': sales,
        'top_customers': top_customers,
        'latest_orders': latest_orders,
        'datas': datas,
        'week':  week,
        'week_amount': week_amount,
        'month': month,
        'month_amount': month_amount,
        'year': year,
        'year_amount': year_amount,
        'today': today_orders,
        'today_amount': today_amount
    }
    return render(request, 'admin_temp/index.html', context)


@login_required
@staff_member_required
def users_admin(request):
    customers = Customer.objects.filter()
    print(customers)
    return render(request, 'admin_temp/users.html', {'users': customers})


@login_required
@staff_member_required
def orders_admin(request):
    orders = Order.objects.filter()
    dBoys = Staff.objects.filter(role='Delivery Boy')
    return render(request, 'admin_temp/orders.html', {'orders': orders, 'dBoys': dBoys})


@login_required
@staff_member_required
def order_view_admin(request, orderID):
    orders = Order.objects.get(id=orderID)
    cart = orders.cart.all()
    dBoys = Staff.objects.filter(role='Delivery Boy')
    return render(request, 'admin_temp/order-details.html', {'order': orders, 'dBoys': dBoys, 'cart': cart})


@login_required
@staff_member_required
def create_orders_admin(request):
    orders = Order.objects.filter()
    dBoys = Staff.objects.filter(role='Delivery Boy')
    print(dBoys)
    return render(request, 'admin_temp/orders.html', {'orders': orders, 'dBoys': dBoys})


@login_required
@staff_member_required
def foods_admin(request):
    foods = Food.objects.filter()
    fCategories = FoodCategories.objects.filter()
    return render(request, 'admin_temp/foods.html', {'foods': foods, 'fCategories': fCategories})


@login_required
@staff_member_required
def food_item_create(request):
    foods = Food.objects.filter()
    fCategories = FoodCategories.objects.filter()
    return render(request, 'admin_temp/create-food.html', {'foods': foods, 'fCategories': fCategories})


@login_required
@staff_member_required
def sales_admin(request):
    sales = Data.objects.filter()
    return render(request, 'admin_temp/sales.html', {'sales': sales})


def menu(request):
    cuisine = request.GET.get('cuisine')
    print(cuisine)
    if cuisine is not None:
        if ((cuisine == "Gujarati") or (cuisine == "Punjabi")):
            foods = Food.objects.filter(status="Enabled", course=cuisine)
        elif(cuisine == "south"):
            foods = Food.objects.filter(
                status="Enabled", course="South Indian")
        elif(cuisine == "fast"):
            foods = Food.objects.filter(course="Fast")
    else:
        foods = Food.objects.filter()
    return render(request, 'menu.html', {'foods': foods, 'cuisine': cuisine})


def index(request):
    food = Food.objects.filter().order_by('-num_order')
    return render(request, 'index.html', {'food': food})


@login_required
@staff_member_required
def confirm_order(request, orderID):
    order = Order.objects.get(id=orderID)
    order.confirmOrder()
    order.save()
    # customerID = order.customer.id
    # customer = Customer.objects.get(id=customerID)
    # customer.total_sale += order.total_amount
    # customer.orders += 1
    # customer.save()
    return redirect('hotel:orders_admin')


@login_required
@staff_member_required
def confirm_delivery(request, orderID):
    to_email = []
    order = Order.objects.get(id=orderID)
    order.confirmDelivery()
    order.save()
    # mail_subject = 'Order Delivered successfully'
    # to = str(order.customer.customer.email)
    # to_email.append(to)
    # from_email = 'pradeepgangwar39@gmail.com'
    # message = "Hi "+order.customer.customer.first_name + \
    #     " Your order was delivered successfully. Please go to your dashboard to see your order history. <br> Your order id is " + \
    #     orderID+". Share ypour feedback woth us."
    # send_mail(
    #     mail_subject,
    #     message,
    #     from_email,
    #     to_email,
    # )
    return redirect('hotel:orders_admin')


@login_required
@staff_member_required
def edit_food(request, foodID):
    food = Food.objects.filter(id=foodID)[0]
    if request.method == "POST":
        if request.POST['base_price'] != "":
            food.base_price = request.POST['base_price']

        if request.POST['discount'] != "":
            food.discount = request.POST['discount']

        food.sale_price = (100 - float(food.discount)) * \
            float(food.base_price)/100

        status = request.POST.get('disabled')
        print(status)
        if status == 'on':
            food.status = "Disabled"
        else:
            food.status = "Enabled"

        food.save()
    return redirect('hotel:foods_admin')


@login_required
@staff_member_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        contact = request.POST['contact']
        email = request.POST['email']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_password']
        username = email.split('@')[0]

        if (first_name == "") or (last_name == "") or (address == "") or (contact == "") or (email == "") or (password == "") or (confirm_pass == ""):
            customers = Customer.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/users.html', {'users': customers, 'error_msg': error_msg})

        if password == confirm_pass:
            user = User.objects.create(
                username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()
            cust = Customer.objects.create(
                customer=user, address=address, contact=contact)
            cust.save()
            success_msg = "New user successfully created"
            customers = Customer.objects.filter()
            return render(request, 'admin_temp/users.html', {'users': customers, 'success_msg': success_msg})

    return redirect('hotel:users_admin')


@login_required
@staff_member_required
def add_food(request):
    if request.method == "POST":
        name = request.POST['name']
        course = request.POST['course']
        status = request.POST['status']
        content = request.POST.get('content', '')
        base_price = request.POST['base_price']
        discount = request.POST['discount']
        category = request.POST['category']
        sale_price = (100 - float(discount)) * float(base_price) / 100
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        # if (name == "") or (course is None) or (status is None) or (content == "") or (base_price == "") or (discount == ""):
        #     foods = Food.objects.filter()
        #     error_msg = "Please enter valid details"
        #     return render(request, 'admin_temp/foods.html', {'foods': foods, 'error_msg': error_msg})

        food = Food.objects.create(name=name, category=category, course=course, status=status, content_description=content,
                                   base_price=base_price, discount=discount, sale_price=sale_price, image=filename)
        food.save()
        foods = Food.objects.filter()
        success_msg = "Please enter valid details"
        return render(request, 'admin_temp/foods.html', {'foods': foods, 'success_msg': success_msg})
    return redirect('hotel:foods_admin')


@login_required
@staff_member_required
def add_deliveryBoy(request, orderID):
    order = Order.objects.get(id=orderID)
    dName = request.POST['deliveryBoy']
    print(dName)
    user = User.objects.get(first_name=dName)
    deliveryBoy = Staff.objects.get(staff_id=user)
    order.delivery_boy = deliveryBoy
    order.save()
    return redirect('hotel:orders_admin')


@login_required
@staff_member_required
def add_sales(request):
    if request.method == "POST":
        date = request.POST['date']
        sales = request.POST['sales']
        expenses = request.POST['expenses']

        if (date is None) or (sales == "") or (expenses == ""):
            sales = Data.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/sales.html', {'sales': sales, 'error_msg': error_msg})

        data = Data.objects.create(date=date, sales=sales, expenses=expenses)
        data.save()
        datas = Data.objects.filter()
        success_msg = "Sales data added successfully!"
        return render(request, 'admin_temp/sales.html', {'sales': datas, 'success_msg': success_msg})

    return redirect('hotel:foods_admin')


@login_required
@staff_member_required
def edit_sales(request, saleID):
    data = Data.objects.filter(id=saleID)[0]
    if request.method == "POST":
        if request.POST['sales'] != "":
            data.sales = request.POST['sales']

        if request.POST['expenses'] != "":
            data.expenses = request.POST['expenses']

        data.save()
    return redirect('hotel:sales_admin')


@login_required
def food_details(request, foodID):
    food = Food.objects.get(id=foodID)
    return render(request, 'user/single.html', {'food': food})


@login_required
def addTocart(request, foodID, userID):
    food = Food.objects.get(id=foodID)
    user = User.objects.get(id=userID)
    cart = Cart.objects.create(food=food, user=user)
    cart.save()
    return redirect('hotel:cart')


@login_required
def delete_item(request, ID):
    item = Cart.objects.get(id=ID)
    item.delete()
    return redirect('hotel:cart')


@login_required
def cart(request):
    user = User.objects.get(id=request.user.id)
    items = Cart.objects.filter(user=user)
    total = 0
    for item in items:
        total += item.food.sale_price
    return render(request, 'cart.html', {'items': items, 'total': total})


@login_required
def placeOrder(request):
    to_email = []
    customer = Customer.objects.get(customer=request.user)
    print(customer.address)
    items = Cart.objects.filter(user=request.user)
    for item in items:
        print(item)
        food = item.food
        order = Order.objects.create(customer=customer, payment_status="Pending",
                                     delivery_status="Pending", total_amount=food.sale_price, payment_method="Cash On Delivery", location=customer.address)
        order.save()
        orderContent = OrderContent(food=food, order=order)
        orderContent.save()
        item.delete()
    # mail_subject = 'Order Placed successfully'
    # to = str(customer.customer.email)
    # to_email.append(to)
    # from_email = 'pradeepgangwar39@gmail.com'
    # message = "Hi "+customer.customer.first_name+" Your order was placed successfully. Please go to your dashboard to see your order history. <br> Your order id is "+order.id+""
    # send_mail(
    #     mail_subject,
    #     message,
    #     from_email,
    #     to_email,
    # )
    return redirect('hotel:cart')


@login_required
def my_orders(request):
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.get(customer=user)
    orders = Order.objects.filter(customer=customer)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def delivery_boy(request):
    user = User.objects.get(id=request.user.id)
    try:
        customer = Customer.objects.get(customer=user)
    except Customer.DoesNotExist:
        staff = Staff.objects.get(staff_id=user)
        if staff is None or staff.role != 'Delivery Boy':
            redirect('hotel:index')
        else:
            orders = DeliveryBoy.objects.filter(delivery_boy=staff)
            return render(request, 'delivery_boy.html', {'orders': orders})

    return redirect('hotel:index')


def order_view_edit(request, orderID):
    orders = Order.objects.get(id=orderID)
    items = Food.objects.all()
    if request.method == "POST":
        staff = Staff.objects.get(staff_id_id=request.user.id)
        created_cart = []
        for index, item in enumerate(request.POST.getlist("product")):
            cart = Cart.objects.create(
                food_id=item, user=request.user, quantity=request.POST.getlist("qty")[index])
            created_cart.append(cart)
        food = cart.food
        order = Order.objects.filter(id=orderID).update(staff=staff, payment_status="Pending",
                                                        note=request.POST.get(
                                                            "note"),
                                                        delivery_status="Pending", total_amount=request.POST.get("net_amount_value"),
                                                        payment_method="Cash On Delivery")
        orders.cart.clear()
        for cart in created_cart:
            orders.cart.add(cart)
        return redirect('/dashboard/admin/orders/')
    return render(request, 'admin_temp/edit-order.html', {'items': items, 'order': orders})


def create_orders_admin(request):
    items = Food.objects.all()
    if request.method == "POST":
        print(request.user.id)
        staff = Staff.objects.get(staff_id_id=request.user.id)
        created_cart = []
        for index, item in enumerate(request.POST.getlist("product")):
            cart = Cart.objects.create(
                food_id=item, user=request.user, quantity=request.POST.getlist("qty")[index])
            created_cart.append(cart)
        food = cart.food
        order = Order.objects.create(staff=staff, payment_status="Pending",
                                     delivery_status="Pending", total_amount=request.POST.get("net_amount_value"), payment_method="Cash On Delivery")
        for cart in created_cart:
            order.cart.add(cart)
        return redirect('/dashboard/admin/orders/')
    return render(request, 'admin_temp/create-order.html', {'items': items})


def get_foods(request):
    items = Food.objects.all().values()
    return JsonResponse({"models_to_return": list(items)})


def get_food_data(request, food_id):
    items = Food.objects.filter(id=food_id)
    items[0].discount = 0
    # items[0]['discount'] = 0
    return JsonResponse({"models_to_return": list(items.values())})


@login_required
@staff_member_required
def stock_items_admin(request):
    RawItems = RawItem.objects.all()
    final_items = []
    for i in RawItems:
        stocks = stock.objects.filter(name=i.id)
        credit = 0
        debit = 0
        name = ''
        weight_types = ''
        for stock_obj in stocks:
            if stock_obj.entry_type == 'CREDIT':
                credit += stock_obj.quantity
            else:
                debit += stock_obj.quantity
            name = stock_obj.name.name
            weight_types = stock_obj.weight_types
        raw_items = {
            "name": name,
            "available": credit - debit,
            "id": i.id,
            "weight_types": weight_types
        }
        final_items.append(raw_items)
    return render(request, 'admin_temp/stock-items.html', {'RawItems': final_items})


@login_required
@staff_member_required
def stock_items_credit_admin(request):
    RawItems = RawItem.objects.all()
    error_msg = ''
    if request.method == "POST":
        staff = Staff.objects.get(staff_id_id=request.user.id)
        name = RawItem.objects.get(id=request.POST['name'])
        description = request.POST['description']
        quantity = request.POST['quantity']
        weight_types = request.POST['weight_types']
        entry_type = request.POST['entry_type']
        bill_no = request.POST['bill_no']
        if (quantity == '0'):
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/stock-credit.html', {'RawItems': RawItems, 'error_msg': error_msg})
        stockCreate = stock.objects.create(
            staff=staff, name=name, description=description, bill_no=bill_no, entry_type=entry_type, quantity=quantity, weight_types=weight_types)
        stockCreate.save()
        return redirect('/dashboard/admin/stock-items/')
    return render(request, 'admin_temp/stock-credit.html', {'RawItems': RawItems, 'error_msg': error_msg})


@login_required
@staff_member_required
def stock_item_details_admin(request, orderID):
    stocks = stock.objects.filter(name=orderID)
    return render(request, 'admin_temp/kitchen-rawItems.html', {'stocks': stocks})


@login_required
@staff_member_required
def stock_item_out_admin(request):
    RawItems = RawItem.objects.all()
    error_msg = ''
    if request.method == "POST":
        staff = Staff.objects.get(staff_id_id=request.user.id)
        name = RawItem.objects.get(id=request.POST['name'])
        description = request.POST['description']
        quantity = request.POST['quantity']
        weight_types = request.POST['weight_types']
        entry_type = request.POST['entry_type']
        if (quantity == '0'):
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/stock-out.html', {'RawItems': RawItems, 'error_msg': error_msg})
        stockCreate = stock.objects.create(
            staff=staff, name=name, description=description, entry_type=entry_type, quantity=quantity, weight_types=weight_types)
        stockCreate.save()
        return redirect('/dashboard/admin/stock-items/')
    return render(request, 'admin_temp/stock-out.html', {'RawItems': RawItems, 'error_msg': error_msg})


def get_order_data(request, order_id):
    print(order_id)
    orders = Order.objects.get(id=order_id)
    items = Food.objects.all()
    query = "select * from Order"
    for p in Order.objects.raw(query):
        print(p.id)
    return render(request, 'admin_temp/print-order.html', {'items': items, 'order': orders})
