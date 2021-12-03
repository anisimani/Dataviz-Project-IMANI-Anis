import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import plotly.express as px
import time
import streamlit.components.v1 as component
from functools import wraps
import altair as alt
import seaborn as sns
from streamlit.proto.Checkbox_pb2 import Checkbox



def get_month(dt):
    return dt.month

def titre(titre):
    return st.title(titre)

def header(head):
    return st.header(head)

def log_time(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(args, **kwargs):

        debut = time.time()
        resultat = func(args, **kwargs)
        fin = time.time()
        f = open("temps.txt",'a',encoding="utf8")
        time_res = fin - debut
        mes = "\n"+func.__name__+ " time = " + str(time_res) + " secondes"
        f.write(mes)
        return resultat

    return wrapper

def graph_bar(abs, ord,databar):
     data=alt.Chart(databar).mark_bar().encode(  x = abs, y = ord)
     data


def graph_line(abs,ord,databar):
    data=alt.Chart(databar).mark_line().encode(x=abs,y=ord)
    data

titre("Exploration Visualisative Individuelle sur le jeu de données 'Demandes de valeurs foncières'")

file_path1= "https://jtellier.fr/DataViz/full_2020.csv"

@st.cache
@log_time   
def read_and_transform1(file_path):
    data=pd.read_csv(file_path, delimiter= ',')


    data['Date/Time']=pd.to_datetime(data['date_mutation'])

    data['month'] = data['Date/Time'].map(get_month)
    
    return data


def sidebar(dictionaire,nom):
    
    return st.sidebar.selectbox(nom,dictionaire)

def slider(nom,valeur1,valeur2):
    st.slider(nom,valeur1,valeur2)

df=read_and_transform1(file_path1)

df = df.sample(10000)
df= df.fillna(0)

def supression():
    df.drop(df.loc[df['code_departement']=='2A'].index, inplace=True)
    df.drop(df.loc[df['code_departement']=='2B'].index, inplace=True)
    
    data = df.drop(df.columns[[0, 2, 3,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,33,35,36]], axis=1)
    return data

df =supression()


def changetype():
    df["code_departement"] = df["code_departement"].astype(str).astype(int)
    df["type_local"] = df["type_local"].astype(str)
    df["nature_culture"] = df["nature_culture"].astype(str)
    #data=df.astype({"surface_reelle_bati":str})
    

changetype()

def pie():
    df_type = df.groupby("type_local")
    st.write(df_type.size())
    a=[]
    for nb,subdf in df_type:
         a.append(subdf.shape[0])
    a.pop(0)
    labels = 'Appartement','Dépendance','Local','Maison'

    fig1, ax1 = plt.subplots()
    ax1.pie(a, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal') 

    st.pyplot(fig1)   



def masksup(nom,valeur1):
    return df.mask(df[nom]<valeur1)

def maskega(nom,valeur2):
    return df.mask(df[nom]!=valeur2)

def histogram(nom,bins,range1,range2):
    hist_values = np.histogram(
        df[nom], bins=bins, range=(range1,range2))[0]
    st.bar_chart(hist_values)

def box(nom1,list1):
    return st.selectbox(nom1,list1)

bar= sidebar({"Accueil" : " ","Département" : df, "Ventes" : df},"Choix page")


if bar== "Accueil":
    header("Aperçu du dataset")
    df

if  bar == "Département":

    if st.checkbox("En fonction du département"):
        departement_selected= st.slider("departement",1,95)
        df_map = maskega("code_departement",departement_selected)
    else:
   
        df_map =df
    
    df_map.dropna(subset = ["latitude"], inplace = True)
    df_map.dropna(subset = ["longitude"], inplace = True)
    st.map(df_map)
    
    header("Valeur fonciere totale")
        
    graph_bar('code_departement','valeur_fonciere',df_map)
        

if bar == "Ventes":

    pie()

   
    header(' Ventes par mois ')
    histogram("month",13,0,13)

    if st.checkbox("En fonction du nombre de m²"):
        valeur = slider("à partir de combien de m² ?",0,500)
    else:
        valeur=0

    df_vente =  masksup('surface_reelle_bati',valeur)
   
    graph_bar('surface_reelle_bati','valeur_fonciere',df_vente)
    

    valeur2=box("Choisisez un type de local",("Maison","Appartement","Dépendance","Local industriel. commercial ou assimilé"))
    df_maison = maskega("type_local",valeur2)
    
    df_maison
    graph_line('surface_reelle_bati','valeur_fonciere',df_maison)
