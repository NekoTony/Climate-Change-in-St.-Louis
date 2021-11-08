from flask import Flask, render_template, send_file
from os.path import exists
import pandas as pd
import json, numbers, collections, re, filecmp, urllib.request, tabula, matplotlib
matplotlib.use('Agg')

app = Flask(__name__, static_url_path="/static", static_folder='static')

@app.route("/")
def hello():
    lpname, dpname = "static/linegraph.png", "static/bargraph.png"
    d = getdata()
    line, bar = generate_plots(d['data'])
    save_plot(line, lpname)
    save_plot(bar, dpname)
    return render_template('index.html')

@app.route("/organizations")
def organization():
    return render_template('organizations.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

def getdata():
    url, tname, fname = "https://www.weather.gov/media/lsx/climate/stl/temp/temp_stl_annual_averages.pdf", "static/temp.pdf", 'static/data.pdf'
    print(download_from_url(url, tname, fname))
    print(convert_data(fname, "static/data.json"))
    d = get_data('static/data.json')
    d = handle_data(d)
    d = get_average(d)
    return d


def download_from_url(url, tempname, finalname):
    urllib.request.urlretrieve(url, tempname)
    if exists(finalname):
        s = filecmp.cmp(tempname, finalname)
        if s:
            return "Data is current, no update."
        else:
            urllib.request.urlretrieve(url, finalname)
            return "New version of data, updated data"

    else:
        urllib.request.urlretrieve(url, finalname)
        return "Didn't exist, created file"

def convert_data(filename, savename, file_type="json"):
    if exists(savename) is False:
        df = tabula.read_pdf(filename, pages='all')[0]
        tabula.convert_into(filename, savename, output_format=file_type, pages='all')
        return "{} has been saved.".format(savename)
    else:
        return 'Files already exists'

def get_data(filename):
    with open(filename, 'r') as f:
        data = f.read()
        json_data = json.loads(data)
    return json_data

def handle_data(data):
    d = get_list('text', data[0]['data'])
    z = []
    for x in d:
        if isinstance(x, list):
            p = [z.isalpha() for z in x]
            if True in p:
                continue
            for y in x:
                p = convert_to_float(x)
                if p is not False:
                    z.append(p)
        else:
            p = convert_to_float(x)
            if p is not False:
                z.append(p)
    z = z[:-1]
    p = []
    for x in z:
        for y in x:
            p.append(y)
    c = 0
    x = ''
    d = {}
    for y in p:
        if c == 0:
            #year
            d[y] = ""
            c += 1
            x = y
        elif c == 1:
            d[x] = y
            c = 0
        else:
            c = 0
    #od = collections.OrderedDict(sorted(d.items()))
    p,z = {},{}
    for k, v in d.items():
        if len(str(k)) == 4:
            k,v = v,k
            z[int(k)] = v
        else:
            p[int(k)] = v
    index = 0
    z = list(z.items())
    od = collections.OrderedDict(sorted(p.items()))
    d = {}
    for k,v in od.items(): d[k] = v

    return d

def get_average(data):
    c = 1
    y, d = '', {'data': []}
    index = 0
    last_year = list(data.items())[-1][0]
    for k,v in data.items():
        if c == 1:
            y = "{}-{}".format(k, k+9)
            d['data'].append([])
            d['data'][index] = {}
            d['data'][index]['years'] = [k]
            d['data'][index]['data'] = [v]
            c += 1
        elif c == 10:
            c = 1
            d['data'][index]['years'].append(k)
            d['data'][index]['data'].append(v)
            d['data'][index]['average'] = average(d['data'][index]['data'])
            d['data'][index]['years'] = y
            del d['data'][index]['data']
            index += 1
        else:
            d['data'][index]['years'].append(k)
            d['data'][index]['data'].append(v)
            c += 1

        if k == last_year:
            if c != 10:
                del d['data'][index]

    return d

def average(d):
    c = 0
    for x in d:
        c += x
    return round(c / len(d),2)

def convert_to_float(d):
    p = []
    for x in d:
        try:
            x = float(x)
            p.append(x)
        except:
            if x == "UNKN":
                x == '0.0'
            p.append(str(x))
    if p == []:
        return False
    return p

def get_list(key, data):
    l = []
    for x in data:
        for y in x:
            l.append(y[key])
    l = [x for x in l if x != '']
    return [y for y in [x.split(' ') for x in l] if y != '']

def generate_plots(data):
    df = pd.DataFrame(data)
    line_plot = df.plot(x='years', y='average', ylim=(54,60))
    bar_plot =  df.plot.barh(x='years', y='average', xlim=(50,60))
    return line_plot, bar_plot

def save_plot(plot, filename):
    fig = plot.get_figure()
    fig.savefig(filename, dpi=300, bbox_inches = "tight")
    return "Success with saving filename".format(filename)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)
