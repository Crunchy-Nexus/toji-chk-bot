import json

# Parse proxies from the file content
proxies_text = """change5.owlproxy.com:7778:SEMlYFF4NT90_custom_zone_US_st__city_sid_48568695_time_5:2895771
change5.owlproxy.com:7778:SEMlYFF4NT90_custom_zone_US_st__city_sid_64165043_time_5:2895771
change5.owlproxy.com:7778:SEMlYFF4NT90_custom_zone_US_st__city_sid_71362438_time_5:2895771
change5.owlproxy.com:7778:SEMlYFF4NT90_custom_zone_US_st__city_sid_43362368_time_5:2895771
change5.owlproxy.com:7778:SEMlYFF4NT90_custom_zone_US_st__city_sid_60730865_time_5:2895771
change5.owlproxy.com:7778:40GLMIkuSa90_custom_zone_BR_st__city_sid_85007785_time_5:2895788
change5.owlproxy.com:7778:40GLMIkuSa90_custom_zone_BR_st__city_sid_36948393_time_5:2895788
change5.owlproxy.com:7778:40GLMIkuSa90_custom_zone_BR_st__city_sid_68490622_time_5:2895788
change5.owlproxy.com:7778:40GLMIkuSa90_custom_zone_BR_st__city_sid_18382663_time_5:2895788
change5.owlproxy.com:7778:40GLMIkuSa90_custom_zone_BR_st__city_sid_66760026_time_5:2895788
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_84337634_time_5:2895809
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_25886053_time_5:2895809
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_74772526_time_5:2895809
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_31514159_time_5:2895809
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_51578811_time_5:2895809"""

# Parse unique proxies
proxies_list = []
seen = set()
for line in proxies_text.strip().split('\n'):
    line = line.strip()
    if line and line not in seen:
        proxies_list.append(line)
        seen.add(line)

# Load config
with open('shopify_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Update proxies
config['proxies'] = proxies_list
config['active_proxies'] = proxies_list[:10]  # Start with first 10 as active
config['dead_proxies'] = []

# Save
with open('shopify_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print(f"✅ Proxies updated!")
print(f"📊 Total proxies: {len(proxies_list)}")
print(f"🟢 Active proxies: {len(config['active_proxies'])}")
print(f"💳 Available sites: {len(config['available_sites'])}")
