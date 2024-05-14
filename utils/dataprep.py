# Package per l'importazione e la preparazione dei dati
# AB_10/05/2024
#
#
# -----------------------------------------------------

import pandas as pd
import streamlit as st 

def upload(messaggio):
    path = st.sidebar.file_uploader(messaggio)
    if not path:
        st.stop()
    df = pd.read_excel(path)
    return df

def sap_raw (df):
        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        df = df[['Liv.','Materiale','Qtà comp. (UMC)','MerceSfusa (BOM)','Ril.Tecn.','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Ril.Prod.','Ril.Ric.','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Materiale':'Articolo','Qtà comp. (UMC)':'Qty'},inplace=True)
        return df

def plm_raw (df):
        df['Liv.']=df['Liv. esplosione'].str.replace('.','')
        #df['Liv.']=df['Liv.'].astype(int)-1
        df = df[['Liv.','Numero componenti','Qtà comp. (UMC)','Merce sfusa','Ril. progettazione','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Rilevante produzione','Cd.parte di ricambio','Testo posizione riga 1',
        'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza']]
        df.rename(columns={'Numero componenti':'Articolo','Qtà comp. (UMC)':'Qty','Merce sfusa':'MerceSfusa (BOM)','Ril. progettazione':'Ril.Tecn.','Rilevante produzione':'Ril.Prod.','Cd.parte di ricambio':'Ril.Ric.'},
                inplace=True)
        #df = df.fillna(0) eliminato 28/12
        df['Liv.']= df['Liv.'].astype(int)
        df['MerceSfusa (BOM)']=df['MerceSfusa (BOM)'].apply(lambda x: 'Sì' if x == 'X' else 'No' )        
        df['Ril.Tecn.']=df['Ril.Tecn.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Prod.']=df['Ril.Prod.'].apply(lambda x: True if x  =='X' else False)
        df['Ril.Ric.']=df['Ril.Ric.'].apply(lambda x: True if x  =='X' else False)      
        return df

def piattaforme_sap(SAP_raw):
    codici_piattaforma = ['P','S','T','Z']
    df = list(set(list(SAP_raw[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in SAP_raw.Articolo.astype(str)]].Articolo)))
    return df

def piattaforme_plm(PLM_raw):
    codici_piattaforma = ['P','S','T','Z']   
    df = list(set(list(PLM_raw[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in PLM_raw.Articolo.astype(str)]].Articolo)))
    return df

