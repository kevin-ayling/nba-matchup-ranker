from datetime import datetime
from nba.aws import write_html



index_file = """<html xmlns="http://www.w3.org/1999/xhtml" >
<head>
    <title>NBA Links</title>
</head>
<body>
  <h1>NBA Games For {}</h1>
  {}
</body>
</html>"""

def map_links(matchups, links):
    link_map = {}
    for matchup in matchups:
        for link in links:
            link_parts = link.split('/')
            link_name = link_parts[4]
            if matchup['teams'][0]['name'].lower() in link_name or matchup['teams'][1]['name'].lower() in link_name:
                link_map[link] = matchup
    return link_map


def generate_html_and_write_to_s3(link_map):
    today = datetime.today()
    header = 'NBA Games for {}, {} {} {}'.format(today.strftime('%A'),
                                                 today.strftime("%B"), today.day,
                                                 today.year)

    index_file_str = index_file.format(header, build_links(link_map))
    write_html(index_file_str, 'index.html')



def build_links(link_map):
    all_links = ''
    for link in link_map:
        link_str = 'href="{}"'.format(link)
        link_time = link_map[link]['time']
        link_header = '{} vs {}'.format(link_map[link]['teams'][0]['name'],link_map[link]['teams'][1]['name'])
        if link_map[link]['tv']['scope'] == 'National':
            link_tag = '<p>{} - <a {} target="_blank">{}</a> - Also on {}</p><br>\n'.format(link_time, link_str, link_header, link_map[link]['tv']['network'])
        else:
            link_tag = '<p>{} - <a {} target="_blank">{}</a></p><br>\n'.format(link_time,link_str, link_header)
        all_links += link_tag
    return all_links


def print_links(link_map):
    for link in link_map:
        print('{} vs. {} - {} - {}'.format(link_map[link]['teams'][0]['name'],link_map[link]['teams'][1]['name'], link_map[link]['time'], link))