#user/bin/python3

#importing files
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import os
import re
import argparse

#reading webpages using urllib
def url_read(webpage):
    uclient = ureq(webpage)
    page_raw = uclient.read()
    uclient.close()
    return page_raw

#fetching city,state,population from the dataset
def city_state_pop_data(row):
    data = values.find_all('td')
    city = data[1].a.text.strip().replace(',',' ')
    city_url = (data[1].a['href'])
    state = data[2].text.strip().replace(',',' ')
    estimate_pop_2018 = data[3].text.strip().replace(',','')
    return (city,state,estimate_pop_2018,city_url)
    
#fetching the high and low average temperature for a respective city        
def get_avg_high_low_temp(city_data_soup,high_low):
    text = "Climate data for"
    tables = city_data_soup.find_all("table",{"class":"wikitable"})
    for table in tables:
        if table.tr.th is not None and text in table.tr.th.text:
            for row in table.find_all('tr')[:-1]:
                if "Average " + high_low in row.th.text:
                    average_high_or_low_row = row.find_all('td')
                    break
            temperature = [float(''.join(values.text.strip().
                            split('(')[0].split()).replace('−','-')) 
                            for values in average_high_or_low_row]
    
            if high_low == 'high':
                return(max(temperature))
                
            return(min(temperature))
        
#fetcing Mayor name for respecitve city            
def get_mayor(city_data_soup):
    tables = city_data_soup.find("table",{"class":"infobox"})
    data = tables.find_all('tr')
    for row in data:
        if row.th is not None and "Mayor" in row.th.text:
            try:
                return(row.td.text.strip().split('[')[0].split('(')[0])
            except:
                return(row.td.text)
            
#Fetching total and land area for respecitve city            
def get_area(city_data_soup):
    tables = city_data_soup.find("table",{"class":"infobox"})
    data = tables.find_all('tr')
    for row in data:
        if row.th is not None and "Area" in row.th:
            total = row.find_next_sibling()
            land = total.find_next_sibling()
            pattern = (r'(\d+(\.\d+)?)')
            total_re = re.findall(pattern,total.td.text.split(' ')[0])
            for value in total_re:
                total_area = value[0]
                break
            
            land_re = re.findall(pattern,land.td.text.split(' ')[0])
            for value in land_re:
                land_area = value[0]
                break
            
    return(total_area,land_area)


#Generating a minimum wage dictionary for each state in the US
def us_min_wage():
    us_minimum_wage_url = ('https://en.wikipedia.org/wiki/\
                            Minimum_wage_in_the_United_States')
    us_minimum_wage_raw = url_read(us_minimum_wage_url)
    us_minimum_wage = soup(us_minimum_wage_raw,"html.parser")
    us_minimum_wage_table = us_minimum_wage.find_all("table",
                                            {"class":"wikitable sortable"})
    
    state_table = us_minimum_wage_table[0]
    minimum_wage_dict = {}
    for value in state_table.find_all('tr')[1:]:
        data = value.find_all('td')
        minimum_wage_dict[data[0].a.text] = data[1].text.split('[')[0]\
                                                        .strip().strip('$')
        
        
    federal_table = us_minimum_wage_table[1]
    fed_data = federal_table.find_all('td')
    minimum_wage_dict[fed_data[0].a.text] = fed_data[1].text.\
                                              split('[')[0].strip().strip('$')
                                              
    minimum_wage_dict['Oregon'] = '10.75'
    minimum_wage_dict['Portland'] = '12.00'
    return minimum_wage_dict
    


if __name__ == "__main__":
    
    #argparsing for selecting the number of top cities' data to be collected.
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-n','--number', help='Input',
                            action = 'store',default = 50)
    

    args = parser.parse_args()
    try:
        number = min(int(args.number),314)
    except :
        number = 50
    
    
    us_city_pop_url = ('https://en.wikipedia.org/wiki/\
                        List_of_United_States_cities_by_population')#selecting cities based on their population rank.
    
    us_city_pop_raw = url_read(us_city_pop_url)
    us_city_soup = soup(us_city_pop_raw,"html.parser")
    us_city_pop_table = us_city_soup.find("table",
                                          {"class":"wikitable sortable"})
    
    outfile = open('top_cities.csv','w')
    outfile.write("City,State,2018 Population Estimate,Minimum Wage($),Average High(°F),Average Low(°F),Mayor,Total Area(sq mi),Land Area(sq mi)\n")
    outfile.close()
    
    
    minimum_wage_dict = us_min_wage()
    base = "https://en.wikipedia.org"

    for idx,values in enumerate(us_city_pop_table.find_all('tr')[1:]):
        if idx < number:
            city,state,estimate_pop_2018,city_url = city_state_pop_data(values)
            city_data = url_read(base+city_url)
            city_data_soup = soup(city_data,"html.parser")
            
            avg_high_temp = get_avg_high_low_temp(city_data_soup,"high")
            avg_low_temp = get_avg_high_low_temp(city_data_soup,"low")
            
            mayor = get_mayor(city_data_soup)
            if mayor is None:
                mayor = 'N.A.'
            total_area,land_area = get_area(city_data_soup)
            
            
            final = [city,state,estimate_pop_2018,\
                         minimum_wage_dict.get(state,'N.A'),\
                         str(avg_high_temp),str(avg_low_temp),\
                         mayor,total_area,land_area]
            print(final)
            
            outfile = open('top_cities.csv','a')
            outfile.write(','.join(final) + "\n")
        else:
            break
        
    outfile.close()    
        
    print("top_cities.csv created in {}".format(os.getcwd()))
    
