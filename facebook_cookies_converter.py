import json

cookies = input("Paste fb cookies here: ")
cookies = cookies.replace("=", ":").replace(";", ",")[:-1]
cookies_dict = {}
cookies = cookies.split(",")

for values in cookies:
    values = values.split(":")
    cookies_dict[values[0]] = values[1]

json_cookies = json.dumps(cookies_dict)

# Specify the file path where you want to save the JSON cookies
file_path = "fb_cookies.json"

# Write the JSON data to the file
with open(file_path, "w") as file:
    file.write(json_cookies)

print(f'\n------------------->> JSON COOKIES SAVED <<---------------------\n\nSaved to: {file_path}\n')
