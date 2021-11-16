from django.shortcuts import render
from django.core.files.storage import default_storage
import random
import string
import datetime
import os




def sale(request):
    time_for_stat = 72  # setting the time for which we want to receive the report
    days = time_for_stat/24+1 #1 day may include 2 calendar days.
    this_month = datetime.datetime.now().strftime("%Y-%m") #current month
    today = datetime.datetime.now() #current day
    delta = datetime.timedelta(days=days)  #setting the day-time for which we want to receive the report
    # get files from dir with sales of this month
    path = '/home/tolik/github/Ridotto-test/ridotto/content/media/' # insert the path to your directory
    directory = path + 'sales/' + this_month #The directory where our reports are stored
    files = os.listdir(directory)  #List of all files in the directory of the current month
    print(files)

    # get all files for last 4 calendar days
    my_stat_files = [] # place for files to create stat
    # We collect all transactions from files for the last 4 days
    for file in files:
        file_created = datetime.datetime.strptime(file.replace('.json',''),"%Y-%m-%d")
        if file_created >= today - delta:  #If the file was created no earlier than 'days' days ago, then add it to our list for further selection
            my_stat_files.append(file)
    print(my_stat_files)



    delta_hours = datetime.timedelta(hours=time_for_stat) # setting the time for which we want to receive the report
    payments_all = [] # place for deals to create stat for the last 'time_for_stat' hours
    total_byers_list = []  # place for buyers to create stat for the last 'time_for_stat' hours
    # We read all the files that we have collected and fill in the list of deals and the list of buyers
    for current_file in my_stat_files:
        with default_storage.open("sales/" + this_month + '/' + current_file, "r") as ins:
            for line in ins:
                deal = eval(line.strip())  #From the dictionary in the str we make a dictionary
                deal_created = datetime.datetime.strptime(deal['date'],"%Y-%m-%d,%H:%M:%S.%f") #date and time of payment
                if today - deal_created <= delta_hours:  #We check that the payment was not earlier than in the last 'time_for_stat' hours
                    payments_all.append(deal)
                    total_byers_list.append(deal['email']) #We initialize buyers by email and add them to our list of buyers


            total_byers = len(set(total_byers_list)) #The total number of buyers for a given period is equal to the length of the set of our 'payments_all' list
            total_payments = len(payments_all)  #The total number of payments

    # checking whether the transaction is completed in the specified time interval
    def check_time(price,pay_created, pay_email):
        h1 = 0 #start time
        h2 = 1 #end time
        minut = 00
        sekund = 00
        for i in range(24):
            if h1 == 23:
                h2 = 23
                minut = 59
                sekund = 59
                print('bingo')
                #if the transaction is completed at the specified time, then we add the necessary data to the dictionary
            if datetime.time(h1, 00) <= pay_created.time() <= datetime.time(h2, minut, sekund):
                if h1 == 23:
                    h2 = 24
                key_time = str(str(h1)+'-'+str(h2))
                print(key_time)
                value_dict_buyers = sales_by_hour[key_time]
                print(value_dict_buyers)
                value_sales = value_dict_buyers[0] + price
                value_buyers = value_dict_buyers[1] + 1
                email_list = value_dict_buyers[2]
                email_list.append(pay_email)
                sales_by_hour[key_time] = [value_sales,value_buyers,email_list]

            h1 += 1
            h2 += 1


    # making a dictionary time in hours : transaction amount
    #Generating a dictionary to store information about purchases by the hour
    # the first value in the list of values is the total amount,
    # the second value is the number of sales
    # the third value is the list of buyers identified by email
    sales_by_hour = {str(x)+'-'+str(x+1):[0,0,[]] for x in range(24)}

    for pay in payments_all:
        pay_created = datetime.datetime.strptime(pay['date'],"%Y-%m-%d,%H:%M:%S.%f")
        price = int(pay['price'].replace('$',''))
        pay_email = pay['email']
        check_time(price,pay_created,pay_email)


    #we go through the dictionary to turn the data on the number of buyers into a pure figure, taking into account repeated purchases by one buyer
    for key,value in sales_by_hour.items():
        num_buyers = len(set(value[2]))
        sales_by_hour[key]= [value[0], value[1], num_buyers]
    print(sales_by_hour)
    return render(request, 'pages/index.html', {'sales_by_hour':sales_by_hour})
