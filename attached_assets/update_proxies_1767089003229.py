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
change5.owlproxy.com:7778:MtJCQzn0dJ00_custom_zone_CO_st__city_sid_51578811_time_5:2895809
change5.owlproxy.com:7778:CM4ZHJXTlUA0_custom_zone_CH_st__city_sid_15289829_time_5:2895907
change5.owlproxy.com:7778:CM4ZHJXTlUA0_custom_zone_CH_st__city_sid_52268102_time_5:2895907
change5.owlproxy.com:7778:CM4ZHJXTlUA0_custom_zone_CH_st__city_sid_46092634_time_5:2895907
change5.owlproxy.com:7778:CM4ZHJXTlUA0_custom_zone_CH_st__city_sid_61393680_time_5:2895907
change5.owlproxy.com:7778:CM4ZHJXTlUA0_custom_zone_CH_st__city_sid_57880946_time_5:2895907
change5.owlproxy.com:7778:0IZtWrIXxT10_custom_zone_GB_st__city_sid_04083119_time_5:2895968
change5.owlproxy.com:7778:0IZtWrIXxT10_custom_zone_GB_st__city_sid_08437554_time_5:2895968
change5.owlproxy.com:7778:0IZtWrIXxT10_custom_zone_GB_st__city_sid_49988761_time_5:2895968
change5.owlproxy.com:7778:0IZtWrIXxT10_custom_zone_GB_st__city_sid_46403352_time_5:2895968
change5.owlproxy.com:7778:0IZtWrIXxT10_custom_zone_GB_st__city_sid_63755681_time_5:2895968
change5.owlproxy.com:7778:X7sB305Nis90_custom_zone_DE_st__city_sid_18014253_time_5:2896025
change5.owlproxy.com:7778:X7sB305Nis90_custom_zone_DE_st__city_sid_80247575_time_5:2896025
change5.owlproxy.com:7778:X7sB305Nis90_custom_zone_DE_st__city_sid_59629707_time_5:2896025
change5.owlproxy.com:7778:X7sB305Nis90_custom_zone_DE_st__city_sid_55483541_time_5:2896025
change5.owlproxy.com:7778:X7sB305Nis90_custom_zone_DE_st__city_sid_33406013_time_5:2896025
change5.owlproxy.com:7778:tyUYnZMUjR10_custom_zone_ID_st__city_sid_25092425_time_5:2896045
change5.owlproxy.com:7778:tyUYnZMUjR10_custom_zone_ID_st__city_sid_26218770_time_5:2896045
change5.owlproxy.com:7778:tyUYnZMUjR10_custom_zone_ID_st__city_sid_04301726_time_5:2896045
change5.owlproxy.com:7778:tyUYnZMUjR10_custom_zone_ID_st__city_sid_26168720_time_5:2896045
change5.owlproxy.com:7778:tyUYnZMUjR10_custom_zone_ID_st__city_sid_22260026_time_5:2896045
change5.owlproxy.com:7778:1I18qkAVb160_custom_zone_IN_st__city_sid_26735880_time_5:2896070
change5.owlproxy.com:7778:1I18qkAVb160_custom_zone_IN_st__city_sid_88801337_time_5:2896070
change5.owlproxy.com:7778:1I18qkAVb160_custom_zone_IN_st__city_sid_13303941_time_5:2896070
change5.owlproxy.com:7778:1I18qkAVb160_custom_zone_IN_st__city_sid_17208023_time_5:2896070
change5.owlproxy.com:7778:1I18qkAVb160_custom_zone_IN_st__city_sid_04896444_time_5:2896070
change5.owlproxy.com:7778:WXfQJxtVrw60_custom_zone_NZ_st__city_sid_15955379_time_5:2896116
change5.owlproxy.com:7778:WXfQJxtVrw60_custom_zone_NZ_st__city_sid_12345816_time_5:2896116
change5.owlproxy.com:7778:WXfQJxtVrw60_custom_zone_NZ_st__city_sid_14813086_time_5:2896116
change5.owlproxy.com:7778:WXfQJxtVrw60_custom_zone_NZ_st__city_sid_22934751_time_5:2896116
change5.owlproxy.com:7778:WXfQJxtVrw60_custom_zone_NZ_st__city_sid_67900355_time_5:2896116"""

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
