#!/usr/bin/env python3
"""Build EN and ZH knowledge graphs from parsed posts."""

import json, re

with open('/home/claude/posts.json') as f:
    posts = json.load(f)

def make_id(text):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text.lower().strip()).strip('-')[:50]

# ============================================================
# EN ENTITY PATTERNS
# ============================================================
EN_COUNTRIES_FROM_TAGS = {
    'australia': 'Australia', 'japan': 'Japan', 'egypt': 'Egypt',
    'hawaii': 'Hawaii', 'canada': 'Canada', 'greece': 'Greece',
    'mexico': 'Mexico', 'italy': 'Italy', 'peru': 'Peru',
    'antarctica': 'Antarctica', 'chile': 'Chile', 'argentina': 'Argentina',
    'alaska': 'Alaska', 'tanzania': 'Tanzania', 'france': 'France',
    'paris': 'France', 'denmark': 'Denmark', 'sweden': 'Sweden',
    'iceland': 'Iceland', 'greenland': 'Greenland', 'faroe': 'Faroe Islands',
    'ecuador': 'Ecuador', 'galápagos': 'Ecuador',
    'colorado': 'Colorado', 'taiwan': 'Taiwan', 'wyoming': 'Wyoming',
    'washington': 'Washington', 'california': 'California', 'oregon': 'Oregon',
    'maine': 'Maine', 'minnesota': 'Minnesota', 'aruba': 'Aruba',
    'cyprus': 'Cyprus', 'germany': 'Germany',
    'french polynesia': 'French Polynesia', 'polynesia': 'French Polynesia',
    'eastern canada': 'Canada', 'beijing': 'China', 'jackson hole': 'Wyoming',
}

EN_PLACES = {
    # Australia
    'darling harbour': 'Darling Harbour', 'bondi beach': 'Bondi Beach',
    'blue mountains': 'Blue Mountains', 'botanic garden': 'Royal Botanic Garden',
    'harbour bridge': 'Harbour Bridge',
    'taronga zoo': 'Taronga Zoo',
    # Japan
    'hakone': 'Hakone', 'kyoto': 'Kyoto', 'tokyo': 'Tokyo',
    'meiji shrine': 'Meiji Shrine', 'fushimi inari': 'Fushimi Inari',
    'kinkaku-ji': 'Kinkaku-ji', 'arashiyama': 'Arashiyama',
    # Egypt
    'cairo': 'Cairo', 'luxor': 'Luxor', 'aswan': 'Aswan',
    'white desert': 'White Desert', 'western desert': 'Western Desert',
    # Greece
    'corfu': 'Corfu Island', 'santorini': 'Santorini', 'athens': 'Athens',
    'oia': 'Oia',
    # Italy
    'siena': 'Siena', 'lucca': 'Lucca', 'pisa': 'Pisa',
    'florence': 'Florence', 'tuscany': 'Tuscany',
    # Peru
    'lima': 'Lima', 'cusco': 'Cusco',
    'sacred valley': 'Sacred Valley', 'tambopata': 'Tambopata',
    'puerto maldonado': 'Puerto Maldonado', 'amazon': 'Amazon Basin',
    # Antarctica / Patagonia
    'punta arenas': 'Punta Arenas', 'torres del paine': 'Torres del Paine',
    'ushuaia': 'Ushuaia', 'tierra del fuego': 'Tierra del Fuego',
    'buenos aires': 'Buenos Aires', 'drake passage': 'Drake Passage',
    'deception island': 'Deception Island',
    # Tanzania
    'serengeti': 'Serengeti', 'ngorongoro': 'Ngorongoro Crater',
    'arusha': 'Arusha', 'tarangire': 'Tarangire',
    'lake manyara': 'Lake Manyara', 'lake eyasi': 'Lake Eyasi',
    'oldupai': 'Oldupai Gorge', 'lake ndutu': 'Lake Ndutu',
    # Greenland
    'ilulissat': 'Ilulissat', 'disko bay': 'Disko Bay',
    'icefjord': 'Ilulissat Icefjord', 'sermeq kujalleq': 'Sermeq Kujalleq',
    'kuannit': 'Kuannit Trail', 'qeqertarsuaq': 'Qeqertarsuaq',
    # Faroe Islands
    'múlafossur': 'Múlafossur Waterfall', 'mulafossur': 'Múlafossur Waterfall',
    'gásadalur': 'Gásadalur', 'gasadalur': 'Gásadalur',
    'sørvágsvatn': 'Sørvágsvatn', 'trælanípa': 'Trælanípa',
    'mykines': 'Mykines', 'kalsoy': 'Kalsoy',
    'kallur': 'Kallur Lighthouse', 'tórshavn': 'Tórshavn',
    'vágar': 'Vágar', 'streymoy': 'Streymoy',
    # Iceland
    'reykjavík': 'Reykjavík', 'reykjavik': 'Reykjavík',
    'keflavík': 'Keflavík', 'keflavik': 'Keflavík',
    # France / Paris
    'latin quarter': 'Latin Quarter', 'left bank': 'Left Bank',
    'eiffel tower': 'Eiffel Tower',
    'champs-élysées': 'Champs-Élysées', 'montmartre': 'Montmartre',
    'tuileries': 'Tuileries Garden', 'les invalides': 'Les Invalides',
    'le marais': 'Le Marais', 'seine': 'Seine River',
    'place de la concorde': 'Place de la Concorde',
    'luxembourg': 'Luxembourg Garden',
    # Copenhagen
    'nyhavn': 'Nyhavn',
    'malmö': 'Malmö', 'roskilde': 'Roskilde',
    # Canada
    'banff': 'Banff', 'jasper': 'Jasper', 'moraine lake': 'Moraine Lake',
    'lake louise': 'Lake Louise', 'lake louis': 'Lake Louise',
    'toronto': 'Toronto', 'ottawa': 'Ottawa', 'montreal': 'Montreal',
    'quebec': 'Quebec City',
    # French Polynesia
    'tahiti': 'Tahiti', 'moorea': 'Moorea', 'bora bora': 'Bora Bora',
    # Easter Island
    'easter island': 'Easter Island',
    # Mexico
    'yucatán': 'Yucatán', 'yucatan': 'Yucatán',
    'los cabos': 'Los Cabos',
    # Colorado
    'telluride': 'Telluride', 'ouray': 'Ouray',
    'grand junction': 'Grand Junction', 'grand mesa': 'Grand Mesa',
    'maroon bells': 'Maroon Bells', 'rocky mountain': 'Rocky Mountain NP',
    'million dollar highway': 'Million Dollar Highway',
    'last dollar road': 'Last Dollar Road', 'aspen': 'Aspen',
    # Alaska
    'kenai': 'Kenai Peninsula', 'seward': 'Seward',
    'anchorage': 'Anchorage', 'fairbanks': 'Fairbanks',
    'denali': 'Denali National Park',
    # Hawaii
    'wailea': 'Wailea', 'road to hana': 'Road to Hana', 'maui': 'Maui',
    # Washington / Oregon
    'mt. rainier': 'Mt. Rainier', 'mount rainier': 'Mt. Rainier',
    'olympic national park': 'Olympic National Park', 'portland': 'Portland',
    # Wyoming
    'jackson hole': 'Jackson Hole', 'grand teton': 'Grand Teton',
    # California / others
    'san diego': 'San Diego', 'pismo beach': 'Pismo Beach',
    'acadia': 'Acadia National Park', 'minneapolis': 'Minneapolis',
    # Galápagos
    'galápagos': 'Galápagos Islands', 'galapagos': 'Galápagos Islands',
    'quito': 'Quito', 'isabela': 'Isabela Island',
    'santa cruz': 'Santa Cruz Island',
    'pinnacle rock': 'Pinnacle Rock', 'bartolomé': 'Bartolomé Island',
    # Valparaíso
    'valparaíso': 'Valparaíso',
    # Aruba
    'aruba': 'Aruba',
}

# Place → Country mapping
PLACE_COUNTRY = {
    'Darling Harbour': 'Australia', 'Bondi Beach': 'Australia', 'Blue Mountains': 'Australia',
    'Royal Botanic Garden': 'Australia', 'Harbour Bridge': 'Australia', 'Taronga Zoo': 'Australia',
    'Hakone': 'Japan', 'Kyoto': 'Japan', 'Tokyo': 'Japan', 'Meiji Shrine': 'Japan', 'Fushimi Inari': 'Japan', 'Arashiyama': 'Japan',
    'Cairo': 'Egypt', 'Luxor': 'Egypt', 'Aswan': 'Egypt', 'White Desert': 'Egypt', 'Western Desert': 'Egypt',
    'Corfu Island': 'Greece', 'Santorini': 'Greece', 'Athens': 'Greece', 'Oia': 'Greece',
    'Siena': 'Italy', 'Lucca': 'Italy', 'Pisa': 'Italy', 'Florence': 'Italy', 'Tuscany': 'Italy',
    'Lima': 'Peru', 'Cusco': 'Peru', 'Sacred Valley': 'Peru', 'Tambopata': 'Peru', 'Puerto Maldonado': 'Peru', 'Amazon Basin': 'Peru',
    'Punta Arenas': 'Chile', 'Torres del Paine': 'Chile', 'Valparaíso': 'Chile',
    'Ushuaia': 'Argentina', 'Buenos Aires': 'Argentina', 'Tierra del Fuego': 'Argentina',
    'Deception Island': 'Antarctica', 'Drake Passage': 'Antarctica',
    'Serengeti': 'Tanzania', 'Ngorongoro Crater': 'Tanzania', 'Arusha': 'Tanzania', 'Tarangire': 'Tanzania', 'Lake Manyara': 'Tanzania', 'Lake Eyasi': 'Tanzania', 'Oldupai Gorge': 'Tanzania', 'Lake Ndutu': 'Tanzania',
    'Ilulissat': 'Greenland', 'Disko Bay': 'Greenland', 'Ilulissat Icefjord': 'Greenland', 'Sermeq Kujalleq': 'Greenland', 'Kuannit Trail': 'Greenland', 'Qeqertarsuaq': 'Greenland',
    'Múlafossur Waterfall': 'Faroe Islands', 'Gásadalur': 'Faroe Islands', 'Sørvágsvatn': 'Faroe Islands', 'Trælanípa': 'Faroe Islands', 'Mykines': 'Faroe Islands', 'Kalsoy': 'Faroe Islands', 'Kallur Lighthouse': 'Faroe Islands', 'Tórshavn': 'Faroe Islands', 'Vágar': 'Faroe Islands', 'Streymoy': 'Faroe Islands',
    'Reykjavík': 'Iceland', 'Keflavík': 'Iceland',
    'Latin Quarter': 'France', 'Left Bank': 'France', 'Eiffel Tower': 'France', 'Champs-Élysées': 'France', 'Montmartre': 'France', 'Seine River': 'France', 'Tuileries Garden': 'France', 'Les Invalides': 'France', 'Le Marais': 'France', 'Place de la Concorde': 'France', 'Luxembourg Garden': 'France',
    'Nyhavn': 'Denmark', 'Roskilde': 'Denmark',
    'Malmö': 'Sweden',
    'Banff': 'Canada', 'Jasper': 'Canada', 'Moraine Lake': 'Canada', 'Lake Louise': 'Canada', 'Toronto': 'Canada', 'Ottawa': 'Canada', 'Montreal': 'Canada', 'Quebec City': 'Canada',
    'Tahiti': 'French Polynesia', 'Moorea': 'French Polynesia', 'Bora Bora': 'French Polynesia',
    'Easter Island': 'Chile',
    'Yucatán': 'Mexico', 'Los Cabos': 'Mexico',
    'Telluride': 'Colorado', 'Ouray': 'Colorado', 'Grand Junction': 'Colorado', 'Grand Mesa': 'Colorado', 'Maroon Bells': 'Colorado', 'Rocky Mountain NP': 'Colorado', 'Million Dollar Highway': 'Colorado', 'Last Dollar Road': 'Colorado', 'Aspen': 'Colorado',
    'Kenai Peninsula': 'Alaska', 'Seward': 'Alaska', 'Anchorage': 'Alaska', 'Fairbanks': 'Alaska', 'Denali National Park': 'Alaska',
    'Wailea': 'Hawaii', 'Road to Hana': 'Hawaii', 'Maui': 'Hawaii',
    'Mt. Rainier': 'Washington', 'Olympic National Park': 'Washington', 'Portland': 'Oregon',
    'Jackson Hole': 'Wyoming', 'Grand Teton': 'Wyoming',
    'San Diego': 'California', 'Pismo Beach': 'California',
    'Acadia National Park': 'Maine', 'Minneapolis': 'Minnesota',
    'Galápagos Islands': 'Ecuador', 'Quito': 'Ecuador', 'Isabela Island': 'Ecuador', 'Santa Cruz Island': 'Ecuador', 'Pinnacle Rock': 'Ecuador', 'Bartolomé Island': 'Ecuador',
    'Aruba': 'Aruba',
    # Museums, Theatres, Opera Houses
    'Sydney Opera House': 'Australia',
    'Egyptian Museum': 'Egypt',
    'Acropolis Museum': 'Greece',
    'Museo Larco': 'Peru',
    'Museum of the North': 'Alaska',
    'Ilulissat Museum': 'Greenland',
    'Qeqertarsuaq Museum': 'Greenland',
    'National Museum of Iceland': 'Iceland',
    'Harpa Concert Hall': 'Iceland',
    'Mill City Museum': 'Minnesota',
    'SMK Museum': 'Denmark',
    'Teatro Colón': 'Argentina',
    'Wright Opera House': 'Colorado',
    'Palais Garnier': 'France',
    'Sacsayhuamán': 'Peru',
}

EN_ACTIVITIES = {
    'hiking': 'Hiking', 'hike': 'Hiking', 'trek': 'Hiking',
    'snorkeling': 'Snorkeling', 'snorkel': 'Snorkeling',
    'diving': 'Diving', 'scuba': 'Diving',
    'boat tour': 'Boat Tour', 'cruise': 'Boat Tour', 'boat ride': 'Boat Tour',
    'kayak': 'Kayaking',
    'safari': 'Safari', 'game drive': 'Safari',
    'dog sled': 'Dog Sledding',
    'snowshoe': 'Snowshoeing',
    'atv': 'ATV Tour',
    'ferry': 'Ferry Travel',
    'whale watch': 'Whale Watching',
}

EN_WILDLIFE = {
    'puffin': 'Atlantic Puffins',
    'whale': 'Whales', 'humpback': 'Humpback Whales',
    'penguin': 'Penguins',
    'seal': 'Seals', 'sea lion': 'Sea Lions',
    'iceberg': 'Icebergs',
    'tortoise': 'Giant Tortoises',
    'iguana': 'Marine Iguanas',
    'booby': 'Blue-footed Boobies', 'boobies': 'Blue-footed Boobies',
    'dolphin': 'Dolphins',
    'flamingo': 'Flamingos',
    'macaw': 'Macaws', 'piranha': 'Piranhas',
    'lion': 'Lions', 'elephant': 'Elephants', 'giraffe': 'Giraffes',
    'zebra': 'Zebras', 'wildebeest': 'Wildebeest',
    'cheetah': 'Cheetahs', 'hippo': 'Hippos',
    'elk': 'Elk', 'moose': 'Moose', 'bear': 'Bears',
    'koala': 'Koalas', 'kangaroo': 'Kangaroos',
    'albatross': 'Albatross', 'stork': 'Storks',
    'monkey': 'Monkeys',
}

EN_FOOD = {
    'seafood': 'Seafood', 'ceviche': 'Ceviche',
    'gelato': 'Gelato', 'pasta': 'Pasta',
    'wine': 'Wine',
    'ræst': 'Ræst', 'ferment': 'Fermented Food',
    'kaffi duus': 'Kaffi Duus',
    'smørrebrød': 'Smørrebrød',
    'sushi': 'Sushi', 'ramen': 'Ramen',
}

EN_ARTS = {
    # Museums & Galleries
    'louvre': 'The Louvre', 'the louvre': 'The Louvre',
    "musée d'orsay": "Musée d'Orsay", 'orsay': "Musée d'Orsay",
    'uffizi': 'Uffizi Gallery',
    'lv foundation': 'LV Foundation', 'louis vuitton foundation': 'LV Foundation',
    'egyptian museum': 'Egyptian Museum',
    'national museum': 'National Museum',
    'orangerie': 'Orangerie Museum',
    'kinokuniya': 'Kinokuniya',
    # Opera Houses & Theatres & Concert Halls
    'opera house': 'Sydney Opera House',
    'palais garnier': 'Palais Garnier', 'paris opera': 'Palais Garnier',
    'teatro colón': 'Teatro Colón', 'teatro colon': 'Teatro Colón',
    'harpa': 'Harpa Concert Hall', 'harpa concert': 'Harpa Concert Hall',
    'tivoli': 'Tivoli Gardens',
}

EN_MONUMENTS = {
    # Egypt
    'pyramids of giza': 'Pyramids of Giza', 'great pyramid': 'Pyramids of Giza',
    'pyramid of khufu': 'Pyramids of Giza', 'pyramid of cheops': 'Pyramids of Giza',
    'sphinx': 'Great Sphinx',
    'karnak': 'Karnak Temple',
    'valley of the kings': 'Valley of the Kings',
    'abu simbel': 'Abu Simbel',
    # Greece
    'acropolis': 'Acropolis', 'parthenon': 'Parthenon',
    'achilleion': 'Achilleion Palace',
    # Peru
    'machu picchu': 'Machu Picchu',
    'sacsayhuamán': 'Sacsayhuamán', 'sacsayhuman': 'Sacsayhuamán',
    'ollantaytambo': 'Ollantaytambo',
    # Mexico
    'chichén itzá': 'Chichén Itzá', 'chichen itza': 'Chichén Itzá',
    'tulum': 'Tulum Ruins',
    # France
    'notre-dame': 'Notre-Dame', 'notre dame': 'Notre-Dame',
    'sacré-cœur': 'Sacré-Cœur', 'sacre coeur': 'Sacré-Cœur',
    'panthéon': 'Panthéon', 'pantheon': 'Panthéon',
    # Iceland
    'hallgrímskirkja': 'Hallgrímskirkja',
    # Denmark
    'rosenborg': 'Rosenborg Castle',
    'kronborg': 'Kronborg Castle', 'frederiksborg': 'Frederiksborg Castle',
    # Italy
    'duomo': 'Duomo',
    'ponte vecchio': 'Ponte Vecchio',
    # Canada
    'château frontenac': 'Château Frontenac',
    # Easter Island
    'moai': 'Moai Statues',
}

ARTS_COUNTRY = {
    'The Louvre': 'France', "Musée d'Orsay": 'France', 'LV Foundation': 'France',
    'Palais Garnier': 'France', 'Orangerie Museum': 'France',
    'Uffizi Gallery': 'Italy',
    'Sydney Opera House': 'Australia',
    'Egyptian Museum': 'Egypt',
    'Teatro Colón': 'Argentina',
    'Harpa Concert Hall': 'Iceland',
    'Tivoli Gardens': 'Denmark',
}

MONUMENT_COUNTRY = {
    'Pyramids of Giza': 'Egypt', 'Great Sphinx': 'Egypt', 'Karnak Temple': 'Egypt',
    'Valley of the Kings': 'Egypt', 'Abu Simbel': 'Egypt',
    'Acropolis': 'Greece', 'Parthenon': 'Greece', 'Achilleion Palace': 'Greece',
    'Machu Picchu': 'Peru', 'Sacsayhuamán': 'Peru', 'Ollantaytambo': 'Peru',
    'Chichén Itzá': 'Mexico', 'Tulum Ruins': 'Mexico',
    'Notre-Dame': 'France', 'Sacré-Cœur': 'France', 'Panthéon': 'France',
    'Hallgrímskirkja': 'Iceland',
    'Rosenborg Castle': 'Denmark', 'Kronborg Castle': 'Denmark', 'Frederiksborg Castle': 'Denmark',
    'Duomo': 'Italy', 'Ponte Vecchio': 'Italy',
    'Château Frontenac': 'Canada',
    'Moai Statues': 'Chile',
}

# ============================================================
# ZH ENTITY PATTERNS
# ============================================================
ZH_COUNTRIES_FROM_TAGS = {
    'australia': '澳大利亚', 'japan': '日本', 'egypt': '埃及',
    'hawaii': '夏威夷', 'canada': '加拿大', 'greece': '希腊',
    'mexico': '墨西哥', 'italy': '意大利', 'peru': '秘鲁',
    'antarctica': '南极洲', 'chile': '智利', 'argentina': '阿根廷',
    'alaska': '阿拉斯加', 'tanzania': '坦桑尼亚', 'france': '法国',
    'paris': '法国', 'denmark': '丹麦', 'sweden': '瑞典',
    'iceland': '冰岛', 'greenland': '格陵兰岛', 'faroe': '法罗群岛',
    'ecuador': '厄瓜多尔', 'galápagos': '厄瓜多尔',
    'colorado': '科罗拉多州', 'taiwan': '台湾', 'wyoming': '怀俄明州',
    'washington': '华盛顿州', 'california': '加利福尼亚', 'oregon': '俄勒冈',
    'maine': '缅因州', 'minnesota': '明尼苏达',
    'aruba': 'Aruba', 'cyprus': '塞浦路斯', 'germany': '德国',
    'french polynesia': '法属波利尼西亚',
    'eastern canada': '加拿大', 'beijing': '中国', 'jackson hole': '怀俄明州',
}

ZH_PLACES = {
    # These patterns match against the combined ZH+EN content
    '达令码头': '达令码头', '邦迪海滩': '邦迪海滩', '蓝山': '蓝山国家公园',
    '皇家植物园': '皇家植物园', '悉尼动物园': '悉尼动物园',
    '箱根': '箱根', '东京': '东京', '京都': '京都',
    '开罗': '开罗', '卢卡索': '卢卡索', '卢克索': '卢卡索', '阿斯旺': '阿斯旺',
    '阿布辛拜': '阿布辛拜神庙', '白色沙漠': '白色沙漠', '西部沙漠': '西部沙漠',
    '金字塔': '吉萨金字塔',
    '科孚岛': '科孚岛', '圣托里尼': '圣托里尼岛', '雅典': '雅典',
    '阿喀琉斯宫': '阿喀琉斯宫',
    '锡耶纳': '锡耶纳', '卢卡': '卢卡', '比萨': '比萨', '佛罗伦萨': '佛罗伦萨',
    '利马': '利马', '库斯科': '库斯科', '马丘比丘': '马丘比丘',
    '圣谷': '圣谷', '亚马逊': '亚马逊平原', 'Tambopata': 'Tambopata',
    'Puerto Maldonado': 'Puerto Maldonado',
    'Punta Arenas': 'Punta Arenas', 'Torres del Paine': 'Torres del Paine',
    '乌斯怀亚': '乌斯怀亚', '火地岛': '火地岛', '布宜诺斯艾利斯': '布宜诺斯艾利斯',
    '德雷克海峡': '德雷克海峡', 'Deception Island': 'Deception Island',
    '塞伦盖蒂': '塞伦盖蒂国家公园', '恩戈罗恩戈罗': '恩戈罗恩戈罗火山',
    '阿鲁沙': '阿鲁沙', '塔兰吉雷': '塔兰吉雷国家公园',
    '马亚拉湖': '马亚拉湖国家公园', '埃亚湖': '埃亚湖',
    '奥杜瓦伊': '奥杜瓦伊峡谷', 'Ndutu': 'Ndutu湖',
    'Ilulissat': 'Ilulissat', 'Disko Bay': 'Disko Bay',
    '冰川峡湾': 'Ilulissat冰川峡湾', 'Sermeq Kujalleq': 'Sermeq Kujalleq冰川',
    'Kuannit': 'Kuannit徒步',
    'Múlafossur': 'Múlafossur瀑布', 'Gásadalur': 'Gásadalur',
    'Sørvágsvatn': 'Sørvágsvatn湖', 'Trælanípa': 'Trælanípa',
    'Mykines': 'Mykines岛', 'Kalsoy': 'Kalsoy岛',
    'Kallur': 'Kallur灯塔', 'Tórshavn': 'Tórshavn',
    'Vágar': 'Vágar岛', 'Drangarnir': 'Drangarnir',
    '雷克雅未克': '雷克雅未克', 'Keflavík': 'Keflavík',
    '拉丁区': '拉丁区', '左岸': '左岸', '塞纳河': '塞纳河',
    '埃菲尔铁塔': '埃菲尔铁塔',
    '蒙马特': '蒙马特高地', '香榭丽舍': '香榭丽舍',
    '荣军院': '荣军院', '玛莱区': '玛莱区',
    '协和广场': '协和广场', '杜乐丽花园': '杜乐丽花园',
    '哥本哈根': '哥本哈根', 'Malmö': 'Malmö', 'Roskilde': 'Roskilde',
    '复活节岛': '复活节岛',
    'Telluride': 'Telluride', 'Ouray': 'Ouray',
    '百万美元公路': '百万美元公路', '大平顶山': '大平顶山',
    'Grand Junction': 'Grand Junction', 'Grand Mesa': '大平顶山',
    '加拉帕戈斯': '加拉帕戈斯群岛', '基多': '基多',
    'Jackson Hole': 'Jackson Hole',
    '尤卡坦': '尤卡坦',
    # Taiwan
    '台南': '台南', '台北': '台北',
}

ZH_ARTS = {
    '卢浮宫': '卢浮宫', '奥赛美术馆': '奥赛美术馆', '橘园美术馆': '橘园美术馆',
    'LV基金会': 'LV基金会',
    '悉尼歌剧院': '悉尼歌剧院', 'Sydney Opera House': '悉尼歌剧院',
    '埃及博物馆': '埃及博物馆', 'Egyptian Museum': '埃及博物馆',
    'Uffizi': 'Uffizi美术馆', '乌菲兹': 'Uffizi美术馆',
    'Harpa': 'Harpa音乐厅', 'Harpa Concert Hall': 'Harpa音乐厅',
    'Teatro Colón': 'Teatro Colón',
    'Palais Garnier': 'Palais Garnier', '巴黎歌剧院': 'Palais Garnier',
    '故宫': '故宫博物院', '故宫博物院': '故宫博物院',
    'Tivoli': 'Tivoli花园',
}

ZH_MONUMENTS = {
    '金字塔': '吉萨金字塔', '狮身人面': '狮身人面像',
    '卡尔纳克': '卡尔纳克神庙', 'Karnak': '卡尔纳克神庙',
    '帝王谷': '帝王谷', '阿布辛拜': '阿布辛拜神庙',
    '阿喀琉斯宫': '阿喀琉斯宫', 'Acropolis': '雅典卫城', '卫城': '雅典卫城',
    '马丘比丘': '马丘比丘', 'Machu Picchu': '马丘比丘',
    'Sacsayhuamán': 'Sacsayhuamán',
    'Chichén Itzá': 'Chichén Itzá', '奇琴伊察': 'Chichén Itzá',
    '圣母院': '巴黎圣母院', 'Notre-Dame': '巴黎圣母院',
    '圣心大教堂': '圣心大教堂',
    'Hallgrímskirkja': 'Hallgrímskirkja教堂',
    'Rosenborg': 'Rosenborg城堡',
    'Duomo': 'Duomo大教堂',
    'Ponte Vecchio': 'Ponte Vecchio老桥',
    '复活节岛石像': 'Moai石像', 'moai': 'Moai石像',
}

ZH_ARTS_COUNTRY = {
    '卢浮宫': '法国', '奥赛美术馆': '法国', '橘园美术馆': '法国', 'LV基金会': '法国',
    'Palais Garnier': '法国',
    '悉尼歌剧院': '澳大利亚',
    '埃及博物馆': '埃及',
    'Uffizi美术馆': '意大利',
    'Harpa音乐厅': '冰岛',
    'Teatro Colón': '阿根廷',
    '故宫博物院': '台湾',
    'Tivoli花园': '丹麦',
}

ZH_MONUMENT_COUNTRY = {
    '吉萨金字塔': '埃及', '狮身人面像': '埃及', '卡尔纳克神庙': '埃及',
    '帝王谷': '埃及', '阿布辛拜神庙': '埃及',
    '阿喀琉斯宫': '希腊', '雅典卫城': '希腊',
    '马丘比丘': '秘鲁', 'Sacsayhuamán': '秘鲁',
    'Chichén Itzá': '墨西哥',
    '巴黎圣母院': '法国', '圣心大教堂': '法国',
    'Hallgrímskirkja教堂': '冰岛',
    'Rosenborg城堡': '丹麦',
    'Duomo大教堂': '意大利', 'Ponte Vecchio老桥': '意大利',
    'Moai石像': '智利',
}

ZH_PLACE_COUNTRY = {
    '达令码头': '澳大利亚', '邦迪海滩': '澳大利亚', '蓝山国家公园': '澳大利亚',
    '皇家植物园': '澳大利亚', '悉尼动物园': '澳大利亚',
    '箱根': '日本', '东京': '日本', '京都': '日本',
    '开罗': '埃及', '卢卡索': '埃及', '阿斯旺': '埃及',
    '白色沙漠': '埃及', '西部沙漠': '埃及',
    '科孚岛': '希腊', '圣托里尼岛': '希腊', '雅典': '希腊',
    '锡耶纳': '意大利', '卢卡': '意大利', '比萨': '意大利', '佛罗伦萨': '意大利',
    '利马': '秘鲁', '库斯科': '秘鲁', '圣谷': '秘鲁',
    '亚马逊平原': '秘鲁', 'Tambopata': '秘鲁', 'Puerto Maldonado': '秘鲁',
    'Punta Arenas': '智利', 'Torres del Paine': '智利',
    '乌斯怀亚': '阿根廷', '火地岛': '阿根廷', '布宜诺斯艾利斯': '阿根廷',
    '德雷克海峡': '南极洲', 'Deception Island': '南极洲',
    '塞伦盖蒂国家公园': '坦桑尼亚', '恩戈罗恩戈罗火山': '坦桑尼亚',
    '阿鲁沙': '坦桑尼亚', '塔兰吉雷国家公园': '坦桑尼亚',
    '马亚拉湖国家公园': '坦桑尼亚', '埃亚湖': '坦桑尼亚',
    '奥杜瓦伊峡谷': '坦桑尼亚', 'Ndutu湖': '坦桑尼亚',
    'Ilulissat': '格陵兰岛', 'Disko Bay': '格陵兰岛',
    'Ilulissat冰川峡湾': '格陵兰岛', 'Sermeq Kujalleq冰川': '格陵兰岛',
    'Kuannit徒步': '格陵兰岛',
    'Múlafossur瀑布': '法罗群岛', 'Gásadalur': '法罗群岛',
    'Sørvágsvatn湖': '法罗群岛', 'Trælanípa': '法罗群岛',
    'Mykines岛': '法罗群岛', 'Kalsoy岛': '法罗群岛',
    'Kallur灯塔': '法罗群岛', 'Tórshavn': '法罗群岛',
    'Vágar岛': '法罗群岛', 'Drangarnir': '法罗群岛',
    '雷克雅未克': '冰岛', 'Keflavík': '冰岛',
    '拉丁区': '法国', '左岸': '法国', '塞纳河': '法国',
    '埃菲尔铁塔': '法国', '蒙马特高地': '法国',
    '香榭丽舍': '法国', '荣军院': '法国',
    '玛莱区': '法国', '协和广场': '法国', '杜乐丽花园': '法国',
    '哥本哈根': '丹麦', 'Roskilde': '丹麦', 'Malmö': '瑞典',
    '复活节岛': '智利',
    'Telluride': '科罗拉多州', 'Ouray': '科罗拉多州',
    '百万美元公路': '科罗拉多州', '大平顶山': '科罗拉多州',
    'Grand Junction': '科罗拉多州',
    '加拉帕戈斯群岛': '厄瓜多尔', '基多': '厄瓜多尔',
    'Jackson Hole': '怀俄明州',
    '尤卡坦': '墨西哥',
    '台南': '台湾', '台北': '台湾',
}

ZH_ACTIVITIES = {
    '徒步': '徒步', '潜水': '潜水', '浮潜': '浮潜',
    '乘船': '游船', '游船': '游船', '邮轮': '游船',
    '渡轮': '渡轮', '狗拉雪橇': '狗拉雪橇', '踏雪': '雪地行走',
    '博物馆': '博物馆参观', '寺庙': '寺庙参观', '教堂': '教堂参观',
    'Safari': 'Safari', 'safari': 'Safari',
}

ZH_WILDLIFE = {
    '海鹦鹉': '海鹦鹉', 'puffin': '海鹦鹉',
    '鲸': '鲸鱼', '座头鲸': '座头鲸',
    '企鹅': '企鹅', '海豹': '海豹', '海狮': '海狮',
    '冰山': '冰山', '象龟': '加拉帕戈斯象龟',
    '鬣蜥': '海鬣蜥', '鲣鸟': '蓝脚鲣鸟',
    '海豚': '海豚', '火烈鸟': '火烈鸟',
    '鹦鹉舔': '金刚鹦鹉', '食人鱼': '食人鱼',
    '狮': '狮子', '大象': '大象', '长颈鹿': '长颈鹿',
    '斑马': '斑马', '角马': '角马', '迁徙': '动物大迁徙',
    '猎豹': '猎豹', '河马': '河马', '鬣狗': '鬣狗',
    '麋鹿': '麋鹿',
}

ZH_FOOD = {
    '海鲜': '海鲜', 'Ræst': 'Ræst', '发酵': '发酵食品',
    'Kaffi Duus': 'Kaffi Duus', '美食': '当地美食',
}

# ============================================================
# GRAPH BUILDER
# ============================================================

# When matching wildlife keywords, longer phrases must take priority.
# Define exclusion rules: if keyword X is found, do NOT match keyword Y.
# This prevents "sea lion" from also triggering "lion".
import re as _re

# Keywords that are substrings of common words and need word-boundary matching
_WORD_BOUNDARY_KW = {
    'lion':  _re.compile(r'\blion\b', _re.IGNORECASE),
    'lions': _re.compile(r'\blions\b', _re.IGNORECASE),
    'seal':  _re.compile(r'\bseals?\b', _re.IGNORECASE),
    'elk':   _re.compile(r'\belks?\b', _re.IGNORECASE),
    'bear':  _re.compile(r'\bbears?\b', _re.IGNORECASE),
}

# After word-boundary match, still exclude if inside a compound like "sea lion"
# or a verb usage like "to bear", "had to bear", "bears some"
WILDLIFE_COMPOUND_EXCLUDES = {
    'lion':  _re.compile(r'\bsea\s+lions?\b', _re.IGNORECASE),
    'lions': _re.compile(r'\bsea\s+lions?\b', _re.IGNORECASE),
    'bear':  _re.compile(r'\b(?:to\s+bear|bear\s+the|bears?\s+some|bears?\s+(?:no|any|little)|colossi\s+bear|bear\s+(?:creek|lake|rd|road|mountain|island|canyon|river|peak|point|gulch))\b', _re.IGNORECASE),
}

def match_wildlife(keyword, search_lower):
    """Match a wildlife keyword with word-boundary awareness."""
    if keyword in _WORD_BOUNDARY_KW:
        if not _WORD_BOUNDARY_KW[keyword].search(search_lower):
            return False
        # Check compound exclusions
        if keyword in WILDLIFE_COMPOUND_EXCLUDES:
            # Only exclude if ALL occurrences are inside compounds
            all_matches = list(_WORD_BOUNDARY_KW[keyword].finditer(search_lower))
            compound_matches = list(WILDLIFE_COMPOUND_EXCLUDES[keyword].finditer(search_lower))
            compound_positions = set()
            for m in compound_matches:
                # Mark positions covered by compound
                for i in range(m.start(), m.end()):
                    compound_positions.add(i)
            # Check if any standalone match exists outside compounds
            for m in all_matches:
                if m.start() not in compound_positions:
                    return True
            return False
        return True
    # For non-ambiguous keywords (including all CJK), use simple substring
    return keyword in search_lower

# Place keywords that are substrings of common words and need word-boundary matching
# e.g. 'quito' inside 'mosquitoes'/'Iquitos', 'oia' inside 'paranoia'
_PLACE_WORD_BOUNDARY = {}
_place_wb_list = ['quito', 'oia', 'lima', 'aspen', 'pisa', 'lucca']
for _kw in _place_wb_list:
    _PLACE_WORD_BOUNDARY[_kw] = _re.compile(r'\b' + _re.escape(_kw) + r'\b', _re.IGNORECASE)

def match_place(keyword, search_text, search_lower):
    """Match a place keyword, using word-boundary regex for ambiguous short keywords."""
    kw_lower = keyword.lower()
    if kw_lower in _PLACE_WORD_BOUNDARY:
        return bool(_PLACE_WORD_BOUNDARY[kw_lower].search(search_lower))
    # Default: simple substring match (works for CJK and unambiguous keywords)
    return keyword in search_text or kw_lower in search_lower

def build_graph(posts, lang):
    nodes = {}
    links = []
    conn_count = {}  # track connections per node
    
    def add_node(nid, label, ntype, url=None):
        if nid not in nodes:
            nodes[nid] = {'id': nid, 'label': label, 'type': ntype}
            conn_count[nid] = 0
            if url:
                nodes[nid]['url'] = url
    
    def add_link(src, tgt):
        pair = (src, tgt)
        if pair not in link_set:
            link_set.add(pair)
            links.append({'s': src, 't': tgt})
            conn_count[src] = conn_count.get(src, 0) + 1
            conn_count[tgt] = conn_count.get(tgt, 0) + 1
    
    link_set = set()
    
    is_en = (lang == 'en')
    CTAGS = EN_COUNTRIES_FROM_TAGS if is_en else ZH_COUNTRIES_FROM_TAGS
    PLACES = EN_PLACES if is_en else ZH_PLACES
    PC = PLACE_COUNTRY if is_en else ZH_PLACE_COUNTRY
    ACTS = EN_ACTIVITIES if is_en else ZH_ACTIVITIES
    WL = EN_WILDLIFE if is_en else ZH_WILDLIFE
    FD = EN_FOOD if is_en else ZH_FOOD
    ARTS = EN_ARTS if is_en else ZH_ARTS
    ARTS_C = ARTS_COUNTRY if is_en else ZH_ARTS_COUNTRY
    MONS = EN_MONUMENTS if is_en else ZH_MONUMENTS
    MONS_C = MONUMENT_COUNTRY if is_en else ZH_MONUMENT_COUNTRY
    
    for post in posts:
        content_field = 'en_content' if is_en else 'zh_content'
        title_field = 'en_title' if is_en else 'zh_title'
        
        content = post[content_field]
        if not content:
            if is_en:
                continue
            else:
                continue
        
        title = post[title_field] or post['en_title'] or 'Untitled'
        
        # Use en_title for ID stability across both graphs
        base_title = post['en_title'] or post['zh_title'] or 'Untitled'
        article_id = 'art-' + make_id(base_title)[:40]
        
        add_node(article_id, title, 'article', post['url'])
        
        # Search both ZH and EN content for entity matching (proper nouns stay in EN within ZH text)
        search_text = content + ' ' + title + ' ' + post['en_content'] + ' ' + post['en_title']
        search_lower = search_text.lower()
        
        # Countries from tags
        found_countries = set()
        for tag in post['tags']:
            tl = tag.lower()
            if tl in CTAGS:
                found_countries.add(CTAGS[tl])
        
        for country in found_countries:
            cid = 'c-' + make_id(country)
            add_node(cid, country, 'country')
            add_link(article_id, cid)
        
        # Places (with substring collision prevention)
        found_places = set()
        matched_keywords = set()
        for kw, place in PLACES.items():
            if match_place(kw, search_text, search_lower):
                found_places.add(place)
                matched_keywords.add(kw)
        
        # Remove false matches where a short keyword is a substring of a longer matched keyword
        # e.g. '卢卡' inside '卢卡索', 'Pisa' inside 'Pismo Beach'
        to_remove = set()
        kw_to_place = {kw: PLACES[kw] for kw in matched_keywords}
        for short_kw in list(matched_keywords):
            for long_kw in matched_keywords:
                if short_kw != long_kw and short_kw in long_kw and kw_to_place[short_kw] != kw_to_place[long_kw]:
                    # Short keyword is substring of long keyword and they map to different places
                    # Check if short keyword appears standalone (not only inside the long keyword)
                    check_text = search_text + ' ' + search_lower
                    # Remove all occurrences of the longer keyword, then check if short still matches
                    cleaned = check_text.replace(long_kw, '').replace(long_kw.lower(), '')
                    if short_kw not in cleaned and short_kw.lower() not in cleaned:
                        to_remove.add(kw_to_place[short_kw])
        found_places -= to_remove
        
        for place in found_places:
            pid = 'p-' + make_id(place)
            add_node(pid, place, 'place')
            add_link(article_id, pid)
            # Link place to country
            if place in PC:
                country = PC[place]
                cid = 'c-' + make_id(country)
                if cid in nodes:
                    add_link(pid, cid)
        
        # Activities
        for kw, act in ACTS.items():
            if kw in search_text or kw.lower() in search_lower:
                aid = 'a-' + make_id(act)
                add_node(aid, act, 'activity')
                add_link(article_id, aid)
        
        # Wildlife (use word-boundary-aware matching)
        for kw, wl in WL.items():
            if match_wildlife(kw, search_lower):
                wid = 'w-' + make_id(wl)
                add_node(wid, wl, 'wildlife')
                add_link(article_id, wid)
        
        # Food
        for kw, fd in FD.items():
            if kw in search_text or kw.lower() in search_lower:
                fid = 'f-' + make_id(fd)
                add_node(fid, fd, 'food')
                add_link(article_id, fid)
        
        # Arts (museums, galleries, theatres, opera houses)
        for kw, arts in ARTS.items():
            if kw in search_text or kw.lower() in search_lower:
                arts_id = 'ar-' + make_id(arts)
                add_node(arts_id, arts, 'arts')
                add_link(article_id, arts_id)
                if arts in ARTS_C:
                    country = ARTS_C[arts]
                    cid = 'c-' + make_id(country)
                    if cid in nodes:
                        add_link(arts_id, cid)
        
        # Monuments & Ruins (古迹)
        for kw, mon in MONS.items():
            if kw in search_text or kw.lower() in search_lower:
                mon_id = 'mn-' + make_id(mon)
                add_node(mon_id, mon, 'monument')
                add_link(article_id, mon_id)
                if mon in MONS_C:
                    country = MONS_C[mon]
                    cid = 'c-' + make_id(country)
                    if cid in nodes:
                        add_link(mon_id, cid)
    
    # Ensure every article has at least one country link
    for nid, node in list(nodes.items()):
        if node['type'] == 'article':
            has_country = any(
                (l['s'] == nid and nodes.get(l['t'], {}).get('type') == 'country') or
                (l['t'] == nid and nodes.get(l['s'], {}).get('type') == 'country')
                for l in links
            )
            if not has_country:
                # Try to infer from title
                pass  # acceptable to leave unlinked for now
    
    # Set sizes based on connections
    for nid, node in nodes.items():
        c = conn_count.get(nid, 0)
        t = node['type']
        if t == 'country':
            node['size'] = min(56, max(30, 30 + c * 2))
        elif t == 'place':
            node['size'] = min(20, max(11, 11 + c))
        elif t == 'activity':
            node['size'] = min(26, max(12, 12 + c * 2))
        elif t == 'wildlife':
            node['size'] = min(22, max(11, 11 + c))
        elif t == 'food':
            node['size'] = min(16, max(11, 11 + c))
        elif t == 'arts':
            node['size'] = min(20, max(11, 11 + c))
        elif t == 'monument':
            node['size'] = min(22, max(11, 11 + c))
        elif t == 'article':
            node['size'] = 14
    
    return {'nodes': list(nodes.values()), 'links': links}

en_graph = build_graph(posts, 'en')
zh_graph = build_graph([p for p in posts if p['zh_content']], 'zh')

graph_data = {'en': en_graph, 'zh': zh_graph}

with open('/home/claude/graph_data.json', 'w', encoding='utf-8') as f:
    json.dump(graph_data, f, ensure_ascii=False)

# Stats
for lang_name, g in [('EN', en_graph), ('ZH', zh_graph)]:
    types = {}
    for n in g['nodes']:
        types[n['type']] = types.get(n['type'], 0) + 1
    print(f"{lang_name}: {len(g['nodes'])} nodes, {len(g['links'])} links")
    print(f"  Types: {types}")
