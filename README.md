## Steam Screenshots Folder Organizer

a python script which takes the location of a steam screenshots folder as input, parses out a steam app id from each
image's filename, retrieves the corresponding app's name from that app's [steamdb.info](http://steamdb.info/) page, and
groups every image by app in separate folders. Retrieved Steam app ID's and their corresponding names are saved to a
.txt file so that they need not be retrieved again.