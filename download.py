from __future__ import with_statement 
import sys
import requests
import json
from easygui import * 
import sqlite3 as lite
import dataset
import wget


if __name__ == '__main__':
	client_id = None
	tag = None
	tag = raw_input("Please enter the tag for download: #")
	client_id = raw_input("Please enter instagram api client_id:")
	image = raw_input("Download images? (y/n):")
	
	if tag == None or tag == "" or client_id == None or client_id == "":
		print "Not a valid tag or client_id"
		sys.exit(1)
	
	
	db = dataset.connect('sqlite:///./db/database.sqlite')
	db.begin()
	db_instagram_table = db['instagram']


	next_url = 'https://api.instagram.com/v1/tags/'+tag+'/media/recent?client_id='+client_id
	while next_url != None:
		r = requests.get(next_url)
		next_url = None
		if r.status_code == 200:
			data = r.json()
			if data['meta']['code']==200:
				picture_dicts = data['data']
				for pic in picture_dicts:
					tags 			=  ",".join(pic['tags']);
					lat = ""
					lan = ""
					print str(pic)
					if pic.has_key('location') and pic['location'] != None:
						lat 			= pic['location']['latitude'];
						lan 			= pic['location']['longitude'];
					created_time 	= pic['created_time'];
					picture_url 	= pic['images']['standard_resolution']['url'];
					url_splits 		= picture_url.split("/")
					picture_file 	= url_splits[len(url_splits)-1]
					post_id 		= pic['id'];
					username 		= pic["user"]["username"];
					caption 		=""
					if pic.has_key('caption') and pic['caption'] != None:
						caption		= pic["caption"]["text"];
					print str(post_id)
					exists = db_instagram_table.find_one(post_id=post_id)
					if not exists:
						print "Inserting"
						insert_data = dict({"post_id":post_id,"lat":lat, "lan":lan , "created_time":created_time, "picture_url":picture_url, "username":username, "caption":caption, "tags":tags, "picture_file":picture_file, "download":0 })
						db_instagram_table.insert(insert_data)     
						db.commit()
						if image == "y":
							wget.download(picture_url, bar=wget.bar_thermometer, out="./pics/"+post_id+".jpg")
							db_instagram_table.update({"post_id":post_id, "download":1}, ["post_id"])  
							db.commit()
					elif image == "y" and exists["download"] == 0:
						wget.download(picture_url, bar=wget.bar_thermometer, out="./pics/"+post_id+".jpg")
						db_instagram_table.update({"post_id":post_id, "download":1}, ["post_id"])  
						db.commit()
					else:
						print "Alredy exists"
						
				if data.has_key("pagination"):
					pagination = data["pagination"]
					if pagination.has_key('next_url'):
						next_url = pagination['next_url']
