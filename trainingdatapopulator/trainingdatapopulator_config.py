__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$8 Oct, 2014 2:10:37 PM$"

import os
curdir = os.getcwd()

cpUrl = 'localhost'
cpSocket = 5008

csLabel = 'ConceptSpace'
attributeLabel = 'Universal'

chunkSize = 500


# Get the main root folder from python paths
# As we are including our root dir in python path for better import, so its a good way to make paths generic

# Process : main_dir is our root dir, Form now hardcoded
# we get the user_defined python paths
# from user_defined python paths we loop and check if condition that last word in python path is our
# root_dir
# if yes than pick up that path if no it will throw list out of index because of [0].

root_dir = 'Smarter.Codes'
user_paths = os.environ['PYTHONPATH'].split(os.pathsep)

#root_dir_path = [k for k in user_paths if root_dir == k.split('/')[-1]][0]
root_dir_path = "~/Smarter.Codes/src"

outputFolder = root_dir_path + '/Universal_Item_Picker/batch_importer/'

apiConceptSpace = "foodweasel.com"

#Check to activate or deactivate log writing
debugging = 1

#CSV file names
nodeFileName = outputFolder + 'nodes.csv'
relationFileName = outputFolder + 'rels.csv'
nodeFileNameTemp = outputFolder + 'nodes.tmp'
relationFileNameTemp = outputFolder + 'rels.tmp'
logFileName = outputFolder + 'log.csv'

#Files to be set for CSV creator resumable
skipListFile = outputFolder + 'skipList.pkl'
universalRowFile = outputFolder + 'universalRow.pkl'
alreadyNERFile = outputFolder + 'alreadyNER.pkl'
alreadyNERListFile = outputFolder + 'alreadyNERList.pkl'
exceptionListFile = outputFolder + 'exceptionList.txt'

osPath = root_dir_path + '/customer_files/foodweasel.com/UIP/'
pathToFiles = osPath + "*.json"

universalNodes = ["next_delivery_time", "geo_tag", "is_rds", "cuisines", "num_ratings", "merchant_type", "street", "is_open", "delivery_percent", "description", "city", "delivery_charge", "short_tag", "zip", "time_needed", "priority", "state", "latitude", "promoted_priority", "type", "laundry_window_minutes", "overall_rating", "last_or_next_order_time", "complete", "distance", "logistics_enabled", "phone", "next_pickup_time", "active", "is_promoted", "recommended_items", "merchant_logo", "type_label", "url", "minutes_left_for_ASAP", "notes", "longitude", "specials", "minimum", "delivery_processes_card", "landmark", "activation_date", "payment_types", "schedule", "price", "increment", "max_qty", "min_qty", "max_price", "max_selection", "min_selection", "sel_dep", "qty_name_singular", "qty_name_plural"]

obtainableList = ["DBPedia>Soda_tax","DBPedia>Benzene_in_soft_drinks","DBPedia>Ice_cream_soda","DBPedia>Spring_(hydrology)","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Cream_soda","DBPedia>Soda_fountain","DBPedia>Soda_fountain","DBPedia>Soda_fountain","DBPedia>Ice_cream_soda","DBPedia>Carbonated_water","DBPedia>Carbonated_water","DBPedia>Carbonated_water","DBPedia>Carbonated_water","DBPedia>Carbonated_water","DBPedia>Carbonated_water","DBPedia>A&W_Cream_Soda","DBPedia>A&W_Cream_Soda","DBPedia>Independent_soda","DBPedia>Soda_gun","DBPedia>Tarhun_(drink)","DBPedia>_Up","DBPedia>Fruktsoda","DBPedia>Ice_cream_soda","DBPedia>Ice_cream_soda","DBPedia>Ice_cream_soda","DBPedia>Big_Soda","DBPedia>Lemon-lime","DBPedia>Traubi","DBPedia>Soda_s%E%BB%AFa_h%E%BB%t_g%C%A","DBPedia>Soda_s%E%BB%AFa_h%E%BB%t_g%C%A","DBPedia>Soda_s%E%BB%AFa_h%E%BB%t_g%C%A","DBPedia>Soda_s%E%BB%AFa_h%E%BB%t_g%C%A","DBPedia>Chanh_mu%E%BB%i","DBPedia>Twin_Lights_Soda","DBPedia>Phosphate_soda","DBPedia>Sarsaparilla_(soft_drink)","DBPedia>Ice_cream_soda","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Soft_drink","DBPedia>Orange_soft_drink","DBPedia>Orange_soft_drink","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Diet_soda","DBPedia>Diet_soda","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Arm_&_Hammer","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Soda_jerk","DBPedia>Soda_jerk","DBPedia>Soda_jerk","DBPedia>Carbonation","DBPedia>Homebrewing","DBPedia>Beer","DBPedia>Beer","DBPedia>Palm_wine","DBPedia>Saltine_cracker","DBPedia>Fried_Coke","DBPedia>Sherbet_(powder)","DBPedia>Soda_shop","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Vault_(soft_drink)","DBPedia>Vault_(soft_drink)","DBPedia>Vault_(soft_drink)","DBPedia>Vault_(soft_drink)","DBPedia>Beaver_Buzz","DBPedia>Beaver_Buzz","DBPedia>Mary_Jane's_Relaxing_Soda","DBPedia>Vitamin_C","DBPedia>Soda_syphon","DBPedia>Soda_syphon","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>Sodastream","DBPedia>IBC_Root_Beer","DBPedia>Surge_(soft_drink)","DBPedia>Tab_(soft_drink)","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>Beat_(soda)","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>OK_Soda","DBPedia>Joya_(drink)","DBPedia>Mug_Root_Beer","DBPedia>Tropicana_Products","DBPedia>Stewart's_Fountain_Classics","DBPedia>Squirt_(soft_drink)","DBPedia>Canfield's_Diet_Chocolate_Fudge","DBPedia>Sunkist_(soft_drink)","DBPedia>Italian_soda","DBPedia>Italian_soda","DBPedia>Moxie","DBPedia>Big_Red_(drink)","DBPedia>Big_Red_(drink)","DBPedia>Cheerwine","DBPedia>Jones_Soda","DBPedia>Brooklyn_Soda_Works","DBPedia>Jones_Soda","DBPedia>Jones_Soda","DBPedia>Jones_Soda","DBPedia>Hubba_Bubba_soda","DBPedia>Hubba_Bubba_soda","DBPedia>Jones_Soda","DBPedia>Hubba_Bubba_soda","DBPedia>Dr._Brown's","DBPedia>Hubba_Bubba_soda","DBPedia>Hubba_Bubba_soda","DBPedia>Nutrisoda","DBPedia>Shasta_(soft_drink)","DBPedia>No-Cal_Soda","DBPedia>Lemonsoda","DBPedia>Grape_soda","DBPedia>Monster_Beverage","DBPedia>Oransoda","DBPedia>Pelmosoda","DBPedia>Salsola_soda","DBPedia>Soda_bread","DBPedia>Soda_bread","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Sodium_bicarbonate","DBPedia>Ice_cream_soda","DBPedia>Sodium_benzoate","DBPedia>Sodium_chloride","DBPedia>Sodium_nitrate","DBPedia>Cornelius_keg","DBPedia>Sodium_silicate","DBPedia>Solanum_aculeastrum","DBPedia>Solanum_aculeastrum","DBPedia>Solanum_aculeastrum","DBPedia>Solanum_aculeastrum","DBPedia>Solanum_aculeastrum","DBPedia>Solanum_viarum","DBPedia>Solanum_viarum","DBPedia>Kali_turgida","DBPedia>Dactyly","DBPedia>Dactyly","DBPedia>Red_La_Soda_(potato)","DBPedia>Soda_pulping","DBPedia>Soda_pulping","DBPedia>Blaesodactylus","DBPedia>Sodium","DBPedia>HeySong_Corporation","DBPedia>Izze","DBPedia>Aspen_Soda","DBPedia>Quatro_(beverage)","DBPedia>Generic_citrus_sodas","DBPedia>Stengah","DBPedia>Stengah","DBPedia>Hosmer_Mountain_Soda","DBPedia>Hosmer_Mountain_Soda","DBPedia>Hosmer_Mountain_Soda","DBPedia>Blue_Sky_Beverage_Company","DBPedia>Beverage_can","DBPedia>Beverage_can","DBPedia>Kroger"]
