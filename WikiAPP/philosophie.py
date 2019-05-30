#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, request, redirect, flash,url_for
from getpage import *
from urllib.parse import unquote
import random
import copy

app = Flask(__name__)

app.secret_key = "512455441210333874512554887546144521zdz"



#################################### Global Variable ##############################
score_dict={}  ## dictionary for score 
first_session="" ## variable to indicate whether it is the first opned session or not
first_page=True ## variable to indicate whether it is the first attenmpt or not
modif=False
parcours="" ## variable to store the history of titles navigation


##################################### index page ###############################
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', message="Bonjour, monde !")


##################################### new game ####################################
# Si vous définissez de nouvelles routes, faites-le ici
@app.route('/new-game', methods=['POST'])
def NewGame():
    global score_dict
    global parcours
    global first_page
    #article=request.form['start']
    parcours=""
    first_page=True
    session['article']=request.form['start']
    session['score']= 0
    session["identifier"]="sessid_"+ str(random.randint(1,1000000))
    score_dict[session["identifier"]]=0
    return redirect('/game' )


############################ Game ########################
@app.route('/game', methods=['GET'])
def Game():
    global first_page 
    global parcours
    title,listhref=getPage(unquote(session['article'])) ### get the title and the listlinks
    print("title " +title)

    ### if it is the first attempt 
    if first_page :
        ### some cases that generate error message
        if len( listhref)==0 or unquote(session['article']).lower()=='philosophie' or title.lower().strip()=='philosophie' or 'philosophie' in list(map(lambda x:x.lower(),listhref)) :
            flash("1ere page ne contient pas de lien ou n'existe pas ou elle qui fait reference directement à la philosophie , votre partie est finie")
            first_page=False
            return redirect('/')
        else :
            print(listhref)
            session['listhref']=listhref
            parcours=parcours + "   >>>   " + title
            first_page=False
            score_dict[session["identifier"]]= score_dict[session["identifier"]]+1 # append the score of the session_id
            session['score']=copy.copy(score_dict[session["identifier"]]) ## get the true session score ( if another page is opened it will not be taken into acount)
            flash('Votre score est %s'%session['score'])
            flash("Votre parcours est : "+ parcours)
            return render_template('game.html',title=title,listeliens=listhref)

    ### if no link or no title found
    elif len( listhref)==0 or title==None :
        flash('Aucun lien ou page trouvé , Vous avez perdu et votre partie est finie')
        return redirect('/')

    ### standard treatment 
    else :
        print(listhref)
        session['listhref']=listhref
        #parcours=parcours + "   >>>   " + title
        return render_template('game.html',title=title,listeliens=listhref)








############################### Move #######################################
@app.route('/move', methods=['POST'])
def Move():
    global modif
    global first_session
    global score_dict
    global parcours

    selectedValue = request.form['destination'] ## get the selected value
    
    if  selectedValue in  session['listhref'] :    ## check if the selected item is in the suggested list   
        #sessionidentifier=request.form['sessionidentifier']
        session['article']=selectedValue # get the selected value
        score_dict[session["identifier"]]= score_dict[session["identifier"]]+1 # append the score of the session_id
        session['score']=copy.copy(score_dict[session["identifier"]]) ## get the true session score ( if another page is opened it will not be taken into acount)
        if  session['article'].lower() =="philosophie": ## check if the selected item is philosophy
            flash('Partie gagnée !!')
            flash('Votre score est %s'%session['score'])
            flash("Votre parcours est : "+ parcours+" > " +"Philosophie") 
            return redirect('/')
        else :                                          ##if the game is not over 
            flash('Votre score est  %s'%session['score'])
            parcours=parcours+ " > " +selectedValue
            flash("Votre parcours est : "+ parcours)

            return redirect('/game')
    else :                                          ## if the selected item is not  in the suggested list
        flash('Vous avez triché et votre partie est finie')
        return redirect('/')






########################### Main ###########################
if __name__ == '__main__':
    app.run(debug=True)

