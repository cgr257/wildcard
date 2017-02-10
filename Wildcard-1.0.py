#!/bin/python

import os,random, sqlite3, datetime, time, argparse
#from datetime import datetime

now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")

def main():
  #parse command line options
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-r", "--rando", help="choose a random episode (this is the default behavior)", action="store_true")
  group.add_argument("-p", "--proximity", help="choose an episode based on the proximity of the internal episode datetime to the current real-world datetime", action="store_true")
  parser.add_argument("-t", "--test", help="use a duplicate test database instead of the regular one", action="store_true")
  parser.add_argument("-c", "--check", help="check to see if the episode has been played recently and skip it if it has", action="store_true")
  args = parser.parse_args()

#connect to DB
  if args.test:
    conn = sqlite3.connect('Wildcard-test.db')
  else:
    conn = sqlite3.connect('Wildcard.db')


  def playshow(chosen_episode):

#Everywhere else in the program, I tried to set it up so that if the program couldnt choose an episode number, I set it 500 which is obviously out of range
#Here you can figure out what to do if the program was unable to find a suitable episode. the best behavior I can think of is to just play episode 45 instead, because it's the best episode there is
#optionally, you could just have the program tell the user to be less selective and then quit gracefully, but that's not as much fun, is it?
    if chosen_episode==500:
      print("you somehow managed not to get an episode, so you're watching nightman. enjoy!")
      chosen_episode=45

    showdata=dbdata(chosen_episode)

    sd_shownumber=showdata[0]
    sd_season=showdata[1]
    sd_episode=showdata[2]
    sd_lastviewed=showdata[3]
    sd_tbc=showdata[4]
    sd_rating=showdata[5]
    sd_title=showdata[6]
    sd_synopsis=showdata[7]
    sd_eday=showdata[8]
    sd_ehour=showdata[9]

    videofile="{}{}".format(str(sd_season).zfill(2),str(sd_episode).zfill(2))

    print("\'{}\'".format(sd_title))
    print("Season {}, Episode {}. Show number {}".format(sd_season,sd_episode,sd_shownumber))
    print("Synopsis:{}\n\n".format(sd_synopsis))

    input("Press Enter to continue...")
 
    dbupdate(sd_shownumber)

    #timed countdown
    #print("Playing in 5...")
    #time.sleep(1)
    #print("4...")
    #time.sleep(1)
    #print("3...")
    #time.sleep(1)
    #print("2...")
    #time.sleep(1)
    #print("1...")
    #time.sleep(1)
    mediaplayer(videofile)

  def mediaplayer(file):
    command=str("mplayer {}.*".format(file))
    os.system(command)

  def randepisode():
    randshow=str(random.randint(1,132))
    return randshow

  def proxepisode():
    #get the current day of the week
    dow = now.strftime("%A")

    #pull all entries from the databse where the internal show date is the same as the current real world date. add all data from each row to a list
    proxrow=[]
    c = conn.cursor()
    c.execute("SELECT * FROM Sunny WHERE epday=?", (dow,))
    while True:
      row = c.fetchone()
      if row == None:
        break
      #append overall episode number (out of 132)
      proxrow_episodedata=[]
      proxrow_episodedata.append(row[0])
      proxrow_episodedata.append(row[1])
      proxrow_episodedata.append(row[2])
      proxrow_episodedata.append(row[3])
      proxrow_episodedata.append(row[4])
      proxrow_episodedata.append(row[5])
      proxrow_episodedata.append(row[6])
      proxrow_episodedata.append(row[7])
      proxrow_episodedata.append(row[8])
      proxrow_episodedata.append(row[9])

      proxrow.append(proxrow_episodedata)

    #this is getting tricky to keep straight because proxrow is a list that contains lists which contain episode data. to access episode numbers you could do this:
    #for listitem in proxrow:
      #print(listitem[0])

    #check the current time of day
    miltime = now.strftime("%H:%M")
    realtime=datetime.datetime.strptime(miltime, '%H:%M')

    #decide which of the pulled shows have an internal time of day that is closest to the current real world time of day
    
    candidates=[]
    for listitem in proxrow:
      episodetime=datetime.datetime.strptime(listitem[9], '%H:%M')
      episodetime_difference=realtime-episodetime
      secondsapart=episodetime_difference.seconds
      
      pair=[secondsapart,listitem[0]]
      candidates.append(pair)
      #print("episode {} takes place at {}, which is {} seconds away from the current time ({})".format(listitem[0], listitem[9], secondsapart, miltime))
    #print(candidates)
    candidates_sorted=sorted(candidates)

    #if check option is set then use it
    if args.check:
      newepisode="no"
      for pair in candidates_sorted:
#        print("the closest episode is episode {} which takes place {} seconds from the current time\n\n".format(candidates_sorted[0][1],candidates_sorted[0][0]))
        print("\nthe closest episode is episode {} which takes place {} seconds from the current time".format(pair[1],pair[0]))
        chosen_episode=pair[1]
        newepisode=dbcheck(chosen_episode)
        if newepisode=="yes":
          return pair[1]
      if newepisode=="no":
        return 500 
    else:
      #set proxshow= the episode number determined in the previous step
      proxshow=str(candidates_sorted[0][1])
      #return chosen episode
      return proxshow

  def dbdata(chosen_episode):
    #gets data about a specified episode from the database
    
    sunnyrow=[]
    c = conn.cursor()
    c.execute("SELECT * FROM Sunny WHERE enumber=?", (chosen_episode,))
    while True:
      row = c.fetchone()
      if row == None:
        break
      #append overall episode number (out of 132)
      sunnyrow.append(row[0])

      #append season number
      sunnyrow.append(row[1])

      #append episode number (within season)
      sunnyrow.append(row[2])

      #append date last viewed
      sunnyrow.append(row[3])

      #append to be continued status (TBC)
      sunnyrow.append(row[4])

      #append rating
      sunnyrow.append(row[5])

      #append episode title
      sunnyrow.append(row[6])

      #append episode synopsis
      sunnyrow.append(row[7])

      #append internal episode day
      sunnyrow.append(row[8])

      #append internal episode time
      sunnyrow.append(row[9])

      return sunnyrow

  def dbcheck(chosen_episode):

    c = conn.cursor()
    c.execute("SELECT * FROM Sunny WHERE enumber=?", (chosen_episode,))
    while True:
      row = c.fetchone()
      if row == None:
        break
      #append overall episode number (out of 132)
      lastviewed=row[3]


    #convert date in database from string to datetime object
    episode_datetime = datetime.datetime.strptime(lastviewed, '%Y-%m-%d')

    #figure out the difference (in days) between the last date the episode was played and the current date
    episode_datetime_difference=now-episode_datetime
    dayssince=episode_datetime_difference.days

    print("episode {} was last played {} days ago".format(chosen_episode,dayssince)) 

    if dayssince > 30:
      return "yes"
    else:
      return "no"

  def dbupdate(chosen_episode):
    #update date last played
    c = conn.cursor()
    c.execute("UPDATE Sunny SET lastviewed = (?) WHERE enumber = (?)", (date, chosen_episode))
    conn.commit()
    conn.close

  if args.proximity:
    print("\n\nchoosing an episode based on the proximity of the internal episode datetime to the current real-world datetime")
    chosen_episode=proxepisode()
    playshow(chosen_episode)
  elif args.rando:
    if args.check:
      newepisode="no"
      counter=0
      while newepisode=="no":
        print("choosing an episode at random")
        chosen_episode=randepisode()
        newepisode=dbcheck(chosen_episode)
        if counter > 150:
          chosen_episode=500
          newepisode="yes"
        counter+=1
      playshow(chosen_episode)
    else:
      print("choosing an episode at random")
      chosen_episode=randepisode()
      playshow(chosen_episode)
  else:
    print("specify either -p or -r. use -h for help")
  

      

if __name__ == '__main__':
  main()
