import requests
from bs4 import BeautifulSoup

inputt='diskit'
response = requests.get(
	url=f"https://en.wikipedia.org/wiki/{inputt}",
)
soup = BeautifulSoup(response.content, 'html.parser')

title = soup.find('td', class_= 'infobox-data').string.strip()
print(title.string)