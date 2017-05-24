

### inputs ###
base_url = "http://losangeles.craigslist.org/search/wst"
min_bdr = 2
min_price = 2000
max_price = 2600

recipients  = ['seanpperry@aol.com', 'l_genung@yahoo.com']
##############


from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup as soup
import re
import smtplib
import time
import sched


all_ids = ['5134213385']



def main():
    
    print 'Launched at ' + str(time.ctime())
    
    check_interval = 5 #minutes
    hours_to_run = 8
    
    query_url = base_url + "/apa?" + "min_price=" + str(min_price) + "&max_price=" + str(max_price) + "&bedrooms=" + str(min_bdr)

    grab_listings(query_url)

    
    scheduler = sched.scheduler(time.time, time.sleep)
    
    for i in range(0, hours_to_run * 12):
        scheduler.enter(i * check_interval * 60, 1, get_send_listings, (query_url,))
    
    scheduler.run()



def get_send_listings(query_url):
    
    print 'Checking for new listings at ' + str(time.ctime())
    
    new_listings = grab_listings(query_url)
    
    if len(new_listings) > 0:
        send_listings(new_listings)
    else:
        print 'No new results at ' + str(time.ctime())



def send_listings(new_listings):
    
    msg = str(len(new_listings)) + ' NEW APARTMENTS FOUND\n\n'
    
    for post in new_listings:
        ret_url = base_url.replace('/search','') + '/apa/'
        link = ret_url + post['id'] + '.html'
        new_post = post['title'] + "\n" + post['nhood'] + "\n" + post['price'] + "\n" + link + "\n\n"
        msg += new_post
    
    fromaddr = 'nousernamesareavailable1@gmail.com'
    username = 'nousernamesareavailable1@gmail.com'

    import ret_pw
    password = ret_pw.pword()
    
    found_server = True
    
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
    except:
        print 'Could not log onto server'
        found_server = False
    
    if found_server:
        for address in recipients:
            try:
                server.sendmail(fromaddr, address, msg)
                print 'Email sent to ' + address + ' at ' + str(time.ctime())
            except:
                print 'Email FAILED to send to ' + address + ' at ' + str(time.ctime())
        server.quit()



def grab_listings(query_url):
    
    raw_html = urlopen(query_url)
    parsed_html = soup(raw_html)
    postings = parsed_html('p')
    
    all_details = []
    
    for post in postings:
        
        new_id = str(post('a')[1]['data-id'])
        
        if len(all_ids) == 1:
            all_ids.append(new_id)
            return []
        
        if new_id in all_ids:
            break
    
        else:
            
            all_ids.append(new_id)
            
            details = {}
            
            details['id'] = new_id
            
            details['title'] = post('a')[1].contents[0]
            #details['time'] = post('span')[0]('time')[0]
            
            try:
                details['nhood'] = scrap_html(post('span')[0]('small')[0])
            except:
                details['nhood'] = 'Not listed'
            
            details['price'] = scrap_html(post.find('span', {'class': 'price'}))
            
            all_details.append(details)
            
            if len(all_details) > 19:
                break

    return all_details



def scrap_html(input):
    
    input = re.sub('<[^<]+?>', '', str(input))
    input = input.replace('(','')
    input = input.replace(')','')
    input = input.strip()
    return input



if __name__ == '__main__':
    
    main()





