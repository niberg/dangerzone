# -*- coding: utf-8 -*-
# Topmenu and the submenus are based of the example found at this location http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/
# The rest of the work was done by Matthew Bennett and he requests you keep these two mentions when you reuse the code :-)
# Basic code refactoring by Andrew Scheller

from time import sleep
from averagedperceptron import *
import curses, os, traceback, praw, codecs, shutil, sys, pickle #curses is the interface for capturing key presses on the menu, os launches the files
try:
  #rmc stuff
  r = praw.Reddit(user_agent='team_marina')
  timestamp_last_post = 0
  recall = 0
  precision = 0
  tp = 0
  tn = 0
  fp = 0
  fn = 0
  #Prevent stupid windows cmd from crashing (hopefully)
  sys.stdout = codecs.getwriter('utf8')(sys.stdout)
  
  screen = curses.initscr() #initializes a new window for capturing key presses
  curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
  curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
  curses.start_color() # Lets you use colors when highlighting selected menu option
  screen.keypad(1) # Capture input from keypad
  
  # Change this to use different colors when highlighting
  curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
  h = curses.color_pair(1) #h is the coloring for a highlighted menu option
  n = curses.A_NORMAL #n is the coloring for a non highlighted menu option
  
  MENU = "menu"
  FUNCTION = "function"
  EXITMENU = "exitmenu"
  
  menu_data = {
    'title': "RMC - Reddit Miner and Classifier", 'type': MENU, 'subtitle': "Please select an option...",
    'options':[
          { 'title': "Download and classify from subreddit...", 'type': MENU, 'subtitle': "Please select subreddit...",
          'options': [
            { 'title': "/r/suicidewatch", 'type': FUNCTION, 'function': '''download_and_classify('suicidewatch')''' },
            { 'title': "/r/rant", 'type': FUNCTION, 'function': '''download_and_classify('rant')''' },
            { 'title': "both", 'type': FUNCTION, 'function': 'print ''''Not implemented'''' },
          ]
          },
    ]
  }
  
  
  
  # This function displays the appropriate menu and returns the option selected
  def runmenu(menu, parent):
  
    # work out what text to display as the last menu option
    if parent is None:
      lastoption = "Exit"
    else:
      lastoption = "Return to %s menu" % parent['title']
  
    optioncount = len(menu['options']) # how many options in this menu
  
    pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
    oldpos=None # used to prevent the screen being redrawn every time
    x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program
  
    # Loop until return key is pressed
    while x !=ord('\n'):
      if pos != oldpos:
        oldpos = pos
        screen.border(0)
        screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
        screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu
  
        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(optioncount):
          textstyle = n
          if pos==index:
            textstyle = h
          screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
        # Now display Exit/Return at bottom of menu
        textstyle = n
        if pos==optioncount:
          textstyle = h
        screen.addstr(5+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
        screen.refresh()
        # finished updating screen
  
      x = screen.getch() # Gets user input
  
      # What is user input?
      if x >= ord('1') and x <= ord(str(optioncount+1)):
        pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
      elif x == 258: # down arrow
        if pos < optioncount:
          pos += 1
        else: pos = 0
      elif x == 259: # up arrow
        if pos > 0:
          pos += -1
        else: pos = optioncount
  
    # return index of the selected item
    return pos
  
    
  # This function calls showmenu and then acts on the selected item
  def processmenu(menu, parent=None):
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu: #Loop until the user exits the menu
      getin = runmenu(menu, parent)
      if getin == optioncount:
          exitmenu = True
      elif menu['options'][getin]['type'] == FUNCTION:
        #curses.def_prog_mode()    # save curent curses environment
        screen.clear()
        eval(menu['options'][getin]['function'])
        # if menu['options'][getin]['title'] == 'Pianobar':
        #   os.system('amixer cset numid=3 1') # Sets audio output on the pi to 3.5mm headphone jack
        # screen.clear() #clears previous screen
        # os.system(menu['options'][getin]['command']) # run the command
        # screen.clear() #clears previous screen on key press and updates display based on pos
        # curses.reset_prog_mode()   # reset to 'current' curses environment
        # curses.curs_set(1)         # reset doesn't do this right
        # curses.curs_set(0)
        # os.system('amixer cset numid=3 2') # Sets audio output on the pi back to HDMI
      elif menu['options'][getin]['type'] == MENU:
            screen.clear() #clears previous screen on key press and updates display based on pos
            processmenu(menu['options'][getin], menu) # display the submenu
            screen.clear() #clears previous screen on key press and updates display based on pos

  def get_submissions(subreddit, limit=20):
      global timestamp_last_post
      submissions = r.get_subreddit(subreddit).get_new(limit=limit)
      new_submissions = []
      reversed = []
      for x in submissions:
          reversed.insert(0, x)
      for x in reversed:
          if x.created <= timestamp_last_post:
              continue
          new_submissions.append(x)
          timestamp_last_post = x.created
          dir = os.getcwd() + "/unknown_submissions/"
          filename = subreddit + '_' + str(x.created) + '.txt'
          file = os.path.join(dir, filename)
          #Don't write unnecessarily
          if os.path.isfile(file):
              continue
          if os.path.isfile(os.path.join("/suicidewatch_submissions/", filename)) or os.path.isfile(os.path.join("/rant_submissions/", filename)):
              continue
          f = codecs.open(file, 'w', 'utf-8')
          f.write(x.title)
          f.write("\n\n")
          f.write(x.selftext)
          f.close()
      return new_submissions
          
  def check_submissions(newsubs, p, subreddit):
      global tp
      global tn
      global fp
      global fn
      global precision
      global recall
      
      if len(newsubs) < 1:
          print "No new submissions!"
          return
      print "You have", len(newsubs), "post(s) to check"   
      for x in newsubs:
          filename = subreddit + "_" + str(x.created) + ".txt"
          print "*" * 80
          print x.title
          print "\n"
          print x.selftext
          features = p.extract_post_features(x.title + "\n\n" + x.selftext)
          prediction = p.predict(features)
          print "*" * 80
          if prediction:
              print "The perceptron thinks this post contains suicidal language."
          else:
              print "The perceptron does not think this post contains suicidal language."
          input = raw_input("Does this post contain suicidal language? yes/no/abort\n")
          while (input.lower() != "yes" and input.lower() != "no" and input.lower() != "abort"):
              print "Please enter yes or no."
              input = raw_input("Does this post contain suicidal language? yes/no/abort\n")
          if input.lower() == "abort":
              print "Aborting..."
              return
          if input.lower() == "yes" and prediction:
              print "Thank you, weights will not be adjusted."
              tp += 1
              #Move to sw folder
              move_classified(filename, "/suicidewatch_submissions/")
          elif input.lower() == "yes" and not prediction:
              print "Thank you, weights will be adjusted."
              p.update(features, False)
              p.save()
              fn += 1
              #Move to sw folder
              move_classified(filename, "/suicidewatch_submissions/")
          elif input.lower() == "no" and not prediction:
              print "Thank you, weights will not be adjusted."
              tn += 1
              #Move to rant folder
              move_classified(filename, "/rant_submissions/")
          elif input.lower() == "no" and prediction:
              print "Thank you, weights will be adjusted."
              p.update(features, False)
              p.save()
              fp += 1
              #Move to rant folder
              move_classified(filename, "/rant_submissions/")
      #Prevent divide by zero error
      if tp > 0:
          precision = float(tp)/(tp + fp)
          recall = float(tp)/(fn + tp)
          fscore = 2 * ((precision * recall)/(precision + recall))
          print "\nTotal combined results:"
          print "Precision: " + str(precision*100) + " %"
          print "Recall: " + str(recall*100) + " %"
          print "F-score: " + str(fscore*100) + " %"
   
  def move_classified(filename, destination):
      shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, filename)) 
              
  def save_bot():
      global timestamp_last_post
      global tp
      global tn
      global fp
      global fn
      global precision
      global recall
      with codecs.open("botsave.pickle", "wb") as file:
          pickle.dump(timestamp_last_post, file, -1)
          pickle.dump(tp, file, -1)
          pickle.dump(tn, file, -1)
          pickle.dump(fp, file, -1)
          pickle.dump(fn, file, -1)
          pickle.dump(precision, file, -1)
          pickle.dump(recall, file, -1)
  
  def load_bot():
      global timestamp_last_post
      global tp
      global tn
      global fp
      global fn
      global precision
      global recall
      with codecs.open("botsave.pickle", "rb") as file:
          timestamp_last_post = pickle.load(file)     
          tp = pickle.load(file)
          tn = pickle.load(file)
          fp = pickle.load(file)
          fn = pickle.load(file)
          precision = pickle.load(file)
          recall = pickle.load(file)
    
  
  def download_and_classify(subreddit):
    screen.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    try:
      load_bot()
    except:
      pass
    p = averagedperceptron()
    try:
      p.load()
    except:
      print "Problem loading perceptron. Exiting..."
      return
    newsubs = get_submissions(subreddit)
    check_submissions(newsubs, p, subreddit)
    save_bot()
    screen = curses.initscr() #initializes a new window for capturing key presses
    curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
    curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
    curses.start_color() # Lets you use colors when highlighting selected menu option
    screen.keypad(1) # Capture input from keypad
    
    # Change this to use different colors when highlighting
    curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
    h = curses.color_pair(1) #h is the coloring for a highlighted menu option
    n = curses.A_NORMAL #n is the coloring for a non highlighted menu option  
    
  # Main program
  processmenu(menu_data)
  screen.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
  os.system('clear')
except:
      # In event of error, restore terminal to sane state.
      screen.keypad(0)
      curses.echo()
      curses.nocbreak()
      curses.endwin()
      traceback.print_exc()           # Print the exception