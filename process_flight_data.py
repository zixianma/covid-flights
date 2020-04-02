import pandas as pd
import matplotlib as mpb
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
import numpy as np
import networkx as nx 
import plotly.express as px
from googletrans import Translator
import geopy
from geopy.geocoders import Nominatim
import plotly.graph_objects as go

#helper function for drawing the bar graph with labels
def autolabel(ax,rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

#helper function for the bar graph
def get_freq_dict(df,prop):
    info_dict = {}
    for key in df[prop]:
        if key in info_dict:
            info_dict[key] += 1
        else: 
            info_dict[key] = 1
    return info_dict

#this function plots a bar graph compatible with labels in Chinese 
def plot_bar(prop,cat_var,freq):
    mfm._rebuild()
    # n = len(mfm.fontManager.ttflist)

    mpb.rcParams['font.family'] = ['Heiti TC']
    width = 0.35
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rect = ax.bar(cat_var, freq, width, color='#4364A2',label=freq)
    ax.set_ylabel('数量')
    ax.set_xlabel(prop)
    ax.set_title(prop + "数量柱状图" )
    autolabel(ax,rect)
    plt.show()

#this function draws bar graph with user input dataframe and property/variable name
def plot_cat_var_bar_graph(df,prop):
    prop_dict = get_freq_dict(df,prop)
    props,props_freq = [], []
    for key, val in prop_dict.items():
        props.append(key)
        props_freq.append(val)
    plot_bar(prop,props,props_freq)


#this function converts a list of flights with city names 
#to one with locations (specificed by (latitude, longitude))
def convert_flights_from_city_to_loc(flights_with_city,city_to_loc_mapping):
    new_flights = []
    for flight in flights_with_city:
        flight_cities = flight.split('-')
        new_flight = [city_to_loc_mapping[city] for city in flight_cities]
        new_flights.append(new_flight)
    return new_flights

#this function draws given flights (with locations) on a world map 
def draw_flights_on_map(flights_with_locs):
    for i in range(len(flights_with_locs)):
        flight = flights_with_locs[i]
        lats = [loc[0] for loc in flight]
        lons = [loc[1] for loc in flight]
        if i == 0:
            fig = go.Figure(go.Scattermapbox(
                mode = "markers+lines",
                lon = lons,
                lat = lats,
                marker = {'size': 10}))
        else:
            fig.add_trace(go.Scattermapbox(
                mode = "markers+lines",
                lon = lons,
                lat = lats,
                marker = {'size': 10}))

    fig.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        mapbox = {
            'center': {'lon': 10, 'lat': 10},
            'style': "stamen-terrain",
            'center': {'lon': -20, 'lat': -20},
            'zoom': 1})

    fig.show()



#this function takes in a dataframe with columns [country,continent,iso_code,flight quota]
#and draws the countries in bubbles on a world map, where the bubble size is proportional 
#to the flight quota
def draw_countries_on_map(df):
    # for i in range(df['国家']):
    #     df['代码'][i] = country_code_mapping[df['国家'][i]]
    fig = px.scatter_geo(df, locations="iso_code", color="continent",
                        hover_name="country", size="flight_quota",
                        projection="natural earth")
    fig.show()



#this function draws the weighted flight graph with all international flights
def draw_flight_graph(weighted_edges_list,node_num,weighted_nodes_list=None):
    G = nx.Graph()
    G.add_weighted_edges_from(weighted_edges_list,alpha=0.5, edge_color='g')
    mfm._rebuild()
    mpb.rcParams['font.family'] = ['Heiti TC']
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(121)
    pos = nx.spring_layout(G,k=0.25)
    
    node_list, node_sizes = [],[]
    if weighted_nodes_list != None:
        for (node, weight) in weighted_nodes_list:
            node_list.append(node)
            node_sizes.append(weight)
        print(len(node_list),len(node_sizes))
        #color codes: #FFD94A (bright yellow); #5BC2E7 (water blue), #4364A2 (darker blue), #D59439 (dark yellow)
        ##E3C25B (dirt yellow)
        nx.draw_networkx_nodes(G, pos, nodelist=node_list,node_size=node_sizes,node_color='#D59439',alpha=1)
        nx.draw_networkx_nodes(G, pos, nodelist=['中国'], node_size=500, node_color='#8C1515', alpha=1)
    else:
        nx.draw_networkx_nodes(G, pos, node_size=500,node_color=range(1,node_num+1),alpha=1,cmap=plt.cm.Blues)
        nx.draw_networkx_nodes(G, pos, nodelist=['中国'], node_size=300, node_color='r', alpha=1)
    for edge in weighted_edges_list:
        nx.draw_networkx_edges(G, pos, edgelist=[edge],width=edge[2]*100, alpha=1, edge_color='#4364A2')
    nx.draw_networkx_labels(G, pos, font_size=7, font_family='Heiti TC',font_weight='bold')
    plt.axis('off')
    plt.show()


def main():
    df = pd.read_excel("民航航班信息.xlsx",encoding='GBK')

    ###### Section 1 ######
    #for drawing the bar graphs for the three variables below
    for prop in ['公司','公司标识','客货标识']:
        plot_cat_var_bar_graph(df,prop)

    ###### Section 2 ######
    #for drawing the weighted graph with all international flights 
    # (i.e. flight_graph_all_final.png & flight_graph_selected_final.png)
    foreign_countries = list(set(df['国家']))
    weekly_quota_dict = {}
    # print(len(foreign_countries))
    total_quota = 0

    #getting the country->weekly flight quota dict 
    for i in range(len(df['国家'])):
        #usually it's just the name of one country, but there can be entries like "英国-德国"
        #add we add this flight's weekly quota to both countries 
        if df['客货标识'][i] == '客货混合':
            countries = []
            country_name = df['国家'][i]
            if "-" in country_name:
                print(country_name)
                if country_name in foreign_countries:
                    foreign_countries.remove(country_name)
                multi_countries = country_name.split('-')
                countries = multi_countries
            else:
                countries = [country_name]
            this_flight_quota = df['周班次'][i]
            for country in countries:
                if country in weekly_quota_dict:
                    weekly_quota_dict[country] += this_flight_quota
                else: 
                    weekly_quota_dict[country] = this_flight_quota
            total_quota += this_flight_quota
    # print(foreign_countries)

    #overwrite the foreign_countries varaible because we only want the countries that have "客货混合" flgihts
    foreign_countries = list(weekly_quota_dict.keys())
    weights = [weekly_quota_dict[country] for country in foreign_countries]
    weighted_edges_list = [('中国',foreign_countries[index],round(weights[index] / total_quota,4)) for index in range(len(foreign_countries))]
   
    df_2 = pd.read_excel('海外华人人口.xlsx')
    populations = []

    for i in range(len(foreign_countries)):
        index_in_df_2 = list(df_2['国家']).index(foreign_countries[i])
        populations.append(df_2['华人人口'][index_in_df_2])
    total = sum(populations)
    weighted_nodes_list = [(foreign_countries[index], round(np.log(populations[index] / total * 10000) * 100,0)) for index in range(len(foreign_countries))]
    draw_flight_graph(weighted_edges_list,len(foreign_countries) + 1,weighted_nodes_list=weighted_nodes_list)

    ###### Section 3 ######
    #for drawing the us-china flights on a world map 
    american_flights = []
    city_names = []
    selected_flights = []
    for i in range(len(df['国家'])):
        if '美国' in df['国家'][i]:
            names = df['航线'][i].split('-')
            american_flights.append(df['航线'][i])
            if df['客货标识'][i] == '客货混合':
                selected_flights.append(df['航线'][i])
            for name in names:
                if name not in city_names:
                    city_names.append(name)
    # print(len(selected_flights),selected_flights)
    
    translations = ['Fuzhou', 'Shanghai Pudong', 'New York Kennedy', 'Los Angeles', 'Taiyuan', 'Chicago', 
    'Beijing Capital', 'San Francisco', 'Washington', 'Guangzhou', 'Shenyang', 'Xiamen', 'Qingdao', 'Anchorage', 
    'Dallas', 'Chengdu', 'Tokyo Narita', 'Shenzhen', 'Osaka Kansai', 'Seoul Incheon', 'Zhengzhou', 'Philadelphia', 
    'Cologne', 'Dubai', 'Almaty', 'Warsaw', 'Bangkok', 'Mumbai', 'Louisville', 'Kuala Lumpur', 'Clark', 
    'Singapore', 'Honolulu', 'Sydney', 'Hahn', 'Cincinnati', 'Miami', 'Zaragoza', 'Hangzhou', 'Vancouver', 
    'Nagoya', 'Hefei', 'Ningbo', 'Wuxi', 'Wuhan', 'Guam', 'Auckland (US)', 'Paris', 'Delhi', 'Penang', 'Hanoi', 
    'Memphis', 'Indianapolis', 'Ho Chi Minh City', 'Jakarta', 'Liege', 'Manila', 'Seattle', 'Halifax', 'Changsha Yellow Flower']
    locs = [None for i in range(len(translations))]
    successes = []
    for i in range(len(translations)):
        geolocator = Nominatim()
        try:
            location = geolocator.geocode(translations[i])
            print(location.address)
            print(loc,(location.latitude, location.longitude))
            print(location.raw)
            locs[i] = (location.latitude, location.longitude)
            successes.append(i)
        except:
            geopy.exc.GeocoderTimedOut
    failures = [translations[i] for i in range(len(translations)) if i not in successes]
    # print(failures)

    city_to_loc_mapping = {}
    for i in range(len(city_names)):
        city_to_loc_mapping[city_names[i]] = locs[i]

    # city_to_loc_mapping = {'福州': (26.07703, 119.283989), '上海浦东': (31.146498, 121.808359), '纽约肯尼迪': (40.64123, -73.777946), 
    # '洛杉矶': (34.055617, -118.263672), '太原': (37.8561856, 112.5561744), '芝加哥': (41.872261, -87.619411), 
    # '北京首都': (4.599466, -74.0786228), '旧金山': (37.7790262, -122.4199061), '华盛顿': (38.8948932, -77.0365529), 
    # '广州': (23.396036, 113.307938), '沈阳': (41.8041094, 123.4276363), '厦门': (24.4758496, 118.0746834), 
    # '青岛': (36.0638034, 120.3781372), '安克雷奇': (61.2163129, -149.8948523), '达拉斯': (32.7762719, -96.7968559), 
    # '成都': (30.6624205, 104.0633219), '东京成田': (35.7118141, 139.7930076), '深圳': (22.555454, 114.0543297), 
    # '大阪关西': (34.69561195, 135.54573383518058), '首尔仁川': (37.44032425, 126.73540046158966), 
    # '郑州': (34.7591877, 113.6524076), '费城': (39.9527237, -75.1635262), '科隆': (50.938361, 6.959974), 
    # '迪拜': (25.0657, 55.1713), '阿拉木图': (43.350122, 77.025204), '华沙': (52.2337172, 21.07141112883227), 
    # '曼谷': (13.7538929, 100.8160803), '孟买': (18.9387711, 72.8353355), '路易斯维尔': (38.2542376, -85.759407), 
    # '吉隆坡': (3.1516964, 101.6942371), '克拉克': (39.3260541, -87.7838526), '新加坡': (1.357107, 103.8194992), 
    # '檀香山': (21.304547, -157.8556764), '悉尼': (-33.939976, 151.175255), '哈恩': (49.9632742, 7.2691209), 
    # '辛辛那提': (39.1014537, -84.5124602), '迈阿密': (25.7742658, -80.1936589), '萨拉戈萨': (41.6521342, -0.8809428), 
    # '杭州': (30.2489634, 120.2052342), '温哥华': (49.2608724, -123.1139529), '名古屋': (35.1851045, 136.8998438), 
    # '合肥': (31.8228094, 117.2218033), '宁波': (29.826881, 121.462363), '无锡': (31.498563, 120.312587), 
    # '武汉': (30.5951051, 114.2999353), '关岛': (13.450125700000001, 144.75755102972062), '奥克兰(美)': (36.5880042, -119.1067762), 
    # '巴黎': (48.8566969, 2.3514616), '德里': (28.637034, 77.190699), '槟城': (5.4065013, 100.2559077), 
    # '河内': (21.027863, 105.833358), '孟菲斯': (35.1490215, -90.0516285), '印第安纳波里斯': (39.7683331, -86.1583502), 
    # '胡志明市': (10.6497452, 106.76197937344351), '雅加达': (-6.1753942, 106.827183), '列日': (50.632831, 5.572304), 
    # '马尼拉': (14.5906216, 120.9799696), '西雅图': (47.6038321, -122.3300624), '哈利法克斯': (44.648618, -63.5859487), 
    # '长沙黄花': (28.196941, 113.220887)}

    flights_with_locs = convert_flights_from_city_to_loc(selected_flights,city_to_loc_mapping)
    draw_flights_on_map(flights_with_locs)


    ###### Section 4 ######
    #for drawing the flight quota of each country on a world map using a bubble chart

    #creating a new df for drawing the world map
    data = {'country': foreign_countries} 
    ppl = []
    continents = []
    iso_codes = []

    df_3 = pd.read_csv('country_code.csv')
    country_to_continent_mapping = {}
    for i in range(len(df_3['country'])):
        if df_3['country'][i] not in country_to_continent_mapping:
            country_to_continent_mapping[df_3['country'][i]] = df_3['continent'][i]

    # not_in = ['Kyrghyzstan', 'Uzbekistan', 'Luxemburg', 'Russia', 'Laos', 'Korea', 'Azerbaijan', 'The United Arab of Emirates', 'Qatar']
    # not_in_continents = ['Asia','Asia','Europe','Asia','Asia','Asia','Europe','Asia','Asia']
    # for i in range(len(not_in)):
    #     country_to_continent_mapping[not_in[i]] = not_in_continents[i]
    my_df = pd.DataFrame(data) 

    for i in range(len(foreign_countries)):
        country = foreign_countries[i]
        index = list(df_2['国家']).index(country)
        ppl.append(weighted_nodes_list[i][1])
        iso_codes.append(df_2['代码'][index])
        country_en = df_2['英文名'][index].rstrip(' ')
        if country_en in country_to_continent_mapping:
            continents.append(country_to_continent_mapping[country_en])
        else: 
            continents.append('Asia')
            print(country_en)
    my_df['flight_quota'] = ppl
    my_df['continent'] = continents
    my_df['iso_code'] = iso_codes

    draw_countries_on_map(my_df)  

if __name__ == "__main__":
    main()