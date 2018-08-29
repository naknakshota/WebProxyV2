#************************************************************************************************
#                                Readme for HW4, COMP 332
#                                 Author: Shota Nakamura
#************************************************************************************************

Files in this Homework:

web_proxy.py
web_client.py
http_constants.py
http_util.py

How to run code:
1.) Save all files in same folder
2.) Run web_proxy.py
3.) Run web_client.py
	i.) Enter URL: cattheory.com
	ii.) First run will return from server
	iii.) Run with same website again
	iv.) Will return from cache. Goes through if loop of 304 Not Modified.
	Note: Will NOT print out 304 modified because what is printed is what is 
	      saved in the cache. The only 304 Modified that is printed out is from 
		  my print statement.
	iii.) Try another website: gabrieldrozdov.com
	