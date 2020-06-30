from django.shortcuts import render, redirect
from .forms import *
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from django.contrib import messages

# urlin = input("Enter url: ")
def get_all_forms(url):
    # Given `url` returns all forms from the HTML content
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):
    # Extracts all possible useful information about an HTML `form`
    details = {}
    # get the form action 
    if form.attrs.get("action") == None:
        action = ""        
    else:
        print(form.attrs.get("action"))
        action = form.attrs.get("action").lower()
    # get the form method (POST, GET, etc.)
    method = form.attrs.get("method", "get").lower()
    # get all the input details such as type and name
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        inputs.append({"type": input_type, "name": input_name})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


def submit_form(form_details, url, value):
    
    # Submits a form given in `form_details`
  
    # construct the full URL 
    target_url = urljoin(url, form_details["action"])
    # get the inputs
    inputs = form_details["inputs"]
    data = {}
    for input in inputs:
        # replace all text and search values with `value`
        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            # if input name and value are not None, 
            # then add them to the data of form submission
            data[input_name] = input_value

    if form_details["method"] == "post":
        return requests.post(target_url, data=data)
    else:
        # GET request
        return requests.get(target_url, params=data)



# Create your views here.

def index(request):
    
    if request.method == 'POST':
        form = UrlForm(request.POST or None)
        
        if form.is_valid():
            url = form.cleaned_data.get('url')
            
            # print(url)
            
    else:
        form = UrlForm()
    context = {
        'form':form,        
    }
    return render(request, 'index.html', context )


# Defining url global variable
url=''

def scan(request):
    
    if request.method == 'POST':
        form = UrlForm(request.POST or None)
        
        if form.is_valid():
            global url
            url = form.cleaned_data.get('url')
            # print(url)
            # print(scan_xss(url))
            return redirect('results')                    
    else:
        form = UrlForm()
        
    context = {
        'form':form,        
    }
    return render(request, 'scanner.html', context)


def scan_results(request, *args, **kwargs):
   
    print('results')
    if url == '':
        return redirect('scan')
    
    
    # Given a `url`, it prints all XSS vulnerable forms and 
    # returns True if any is vulnerable, False otherwise
    
    # get all the forms from the URL
    forms = get_all_forms(url)
    print(f"Detected {len(forms)} forms on {url}.")
    form_lenght = len(forms)
    if form_lenght == 0:
        messages.error(request, "No form found!")
        return redirect('scan')
    
    # Changes
    # js_script = "<Script>alert('hi')</scripT>"
    js_script = "<Script>alert('hi')</scripT>"
    
    # returning value
    is_vulnerable = False
    
    # iterate over all forms
    for form in forms:
        form_details = get_form_details(form)
        print(form_details)
        content = submit_form(form_details, url, js_script).content.decode()
        if js_script in content:
            print(f"XSS Detected on {url}")
            print(f"Form details:")
            pprint(form_details)
            is_vulnerable = True
        print(is_vulnerable)     
        
    context={
        'url':url,
        'forms':form_lenght,
        'details':[form_details],
        'vul':is_vulnerable,
        
    }
    return render(request, 'results.html', context)


