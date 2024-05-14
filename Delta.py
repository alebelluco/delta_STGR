# v0.0 del 10-05-2024
# -------------------
# App per l'estrazione degli articoli da correggere per il campo STGR

# APPUNTI
# ---------
# Isolare livello V
# Piattaforme: dopo che ho solo i codici con STGR popolato, merge con nuovo codice piattaforma, poi merge con MY25, restano solo i codici non match, così riduco l'analisi


import streamlit as st
import pandas as pd 
from utils import dataprep as dp 
from utils import print as pr
from utils import bom
import numpy as np

st.set_page_config(layout="wide")

layout = {

    'Transcodifica' : ['Articolo','Articolo MY24'],
     
    'STGR':{'cols':['Liv.','Articolo','Testo breve oggetto','Qty','STGR','Testo posizione riga 1'],
            'w':1000,
            'h':400},

    'Motore':{'cols':['Liv.','Articolo','Testo breve oggetto','elimina'],
            'w':1000, 
            'h':1000},
    
    'Piattaforme' : {'cols': ['key','Piattaforma','Liv.','Articolo','Testo breve oggetto','Qty','STGR','Testo posizione riga 1'],
                    'w':1000, 
                    'h':400},



    'Piattaforme25' : {'cols': ['Piattaforma','Desc_piattaforma','Piattaforma MY24','MY25 vs MY24','Nota','Liv.','Articolo','Testo breve oggetto','Qty','STGR_MY25','Testo posizione riga 1_MY25','STGR_MY24','Testo posizione riga 1_MY24'],
                    'w':2000, 
                    'h':600},

    'Merge_piattaforme' : ['key','STGR','Testo posizione riga 1'],

    'Merge_no_piatt' : ['key','STGR','Testo posizione riga 1'],

    'No_piatt' :  {'cols': ['L1','Nota','Liv.','Articolo','Testo breve oggetto','Qty','STGR_MY25','Testo posizione riga 1_MY25','STGR_MY24','Testo posizione riga 1_MY24'],
                    'w':2000, 
                    'h':600},


}

TRANSCODIFICA, COMPARE_P, OTHER = st.tabs(['Transcodifica','Compare piattaforme', 'Livelli M-V-X'])

sap_raw = dp.upload('Caricare D33')
df_SAP = dp.sap_raw(sap_raw)
df_SAP = bom.rimuovi_motore(df_SAP)
plm_raw = dp.upload('Caricare BOM PLM')
df_PLM = dp.plm_raw(plm_raw)
df_PLM = bom.rimuovi_motore(df_PLM)

sku = df_SAP.Articolo.iloc[0]


def callback():
    new =  work.copy()
    codici = df_SAP_not_PLM.copy()
    codici = codici.rename(columns={'Articolo':'Articolo MY24'})
    new = new.merge(codici, how='left',left_on='Descrizione MY24', right_on = 'Testo breve oggetto')
    new = new.drop(columns=['Testo breve oggetto_y','Articolo MY24_x'])
    new = new.rename(columns={'Articolo MY24_y':'Articolo MY24', 'Testo breve oggetto_x':'Testo breve oggetto'})
    new['Articolo MY24'] = np.where(new['Descrizione MY24'].astype(str)=='Piattaforma non presente in MY24','ND',new['Articolo MY24'])
    st.session_state.tabella = new
   
with TRANSCODIFICA:
    placeholder = st.empty()
    if not st.toggle('Transcodifica disponibile, carica file'):
        codici_piattaforma = ['P','S','T','Z']
        piattaforme_SAP = list(set(list(df_SAP[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in df_SAP.Articolo.astype(str)]].Articolo)))
        piattaforme_PLM = list(set(list(df_PLM[[any(digit in articolo[3:4] for digit in codici_piattaforma)for articolo in df_PLM.Articolo.astype(str)]].Articolo)))
        SAP_not_PLM = list(set(piattaforme_SAP).difference(piattaforme_PLM))
        PLM_not_SAP = list(set(piattaforme_PLM).difference(piattaforme_SAP))

        colA, colB = st.columns([1,1])

        with colA:
            st.subheader('Codici piattaforma in MY24 e NON in MY25', divider='gray')
            df_SAP_not_PLM = pd.DataFrame(SAP_not_PLM)
            df_SAP_not_PLM = df_SAP_not_PLM.rename(columns={0:'Articolo'})
            df_SAP_not_PLM = df_SAP_not_PLM.merge(df_SAP[['Articolo','Testo breve oggetto']], how='left',left_on='Articolo',right_on='Articolo')
            descrizioni = list(df_SAP_not_PLM['Testo breve oggetto'])
            descrizioni.append('Piattaforma non presente in MY24')
            st.dataframe(df_SAP_not_PLM, height=800)
            
        with colB:
            st.subheader(':red[Codici piattaforma in MY25 e NON in MY24]', divider ='red')
            df_PLM_not_SAP = pd.DataFrame(PLM_not_SAP)
            df_PLM_not_SAP = df_PLM_not_SAP.rename(columns={0:'Articolo'})
            df_PLM_not_SAP = df_PLM_not_SAP.merge(df_PLM[['Articolo','Testo breve oggetto']], how='left',left_on='Articolo',right_on='Articolo')
            df_PLM_not_SAP['Descrizione MY24']=None
            df_PLM_not_SAP['Articolo MY24']=None

            if 'tabella' not in st.session_state:
                st.session_state.tabella = df_PLM_not_SAP.copy()

            work = st.session_state.tabella.copy()
            work = st.data_editor(work, column_config={'Descrizione MY24':st.column_config.SelectboxColumn(options=descrizioni)},height=800)
            submit_button = st.button('Inserisci',on_click=callback)

        st.subheader('Download del file di transcodifica piattaforme MY24-MY25',divider='grey')
        pr.scarica_excel(st.session_state.tabella, f'{sku} - Transcodifica.xlsx')

        transcod = st.session_state.tabella.copy()
        
    else:
        path_trascodifica = st.file_uploader('Caricare file transcodifica')
        if not path_trascodifica:
            st.warning('Caricare il file di transcodifica')
            st.stop()  

        transcod = pd.read_excel(path_trascodifica)
        st.write(transcod)

    with placeholder:
        if not st.toggle('Abilita prosecuzione'):
            st.stop()   
     
with COMPARE_P:

    transcod = transcod[layout['Transcodifica']]
    transcod = transcod.rename(columns={'Articolo':'Piattaforma','Articolo MY24':'Piattaforma MY24'})
    #st.write(transcod)
    SAP, PLM = st.columns([1,1])

    with SAP:
                
        df_SAP_nomotore = bom.rimuovi_motore(df_SAP)

        df_sap_piatt = bom.estrai_piattaforme(df_SAP_nomotore)[0]
        df_sap_no_piatt = bom.estrai_piattaforme(df_SAP_nomotore)[1]

        # da qui posso filtrare solo i codici con STGR popolato
        #if st.toggle('Filtra solo righe con STGR popolato'):
        #    df_sap_piatt = df_sap_piatt[df_sap_piatt.STGR.astype(str)!='nan']
        
        df_sap_piatt['STGR']=df_sap_piatt['STGR'].fillna('Non popolato in MY24')
        df_sap_piatt['key'] = df_sap_piatt['Piattaforma']+df_sap_piatt['Articolo']
        #pr.stampa(df_sap_piatt, 'SAP (MY24) | Piattaforme',layout, 'Piattaforme')

        #if st.toggle('Filtra solo righe con STGR popolato',key='sap_no_piatt'):
        #        df_sap_no_piatt = df_sap_no_piatt[df_sap_no_piatt.STGR.astype(str)!='nan']

        
        

        #pr.stampa(df_sap_no_piatt, 'SAP no piattaforme',layout,'STGR')

    with PLM:

        df_PLM_nomotore = bom.rimuovi_motore(df_PLM)

        df_plm_piatt = bom.estrai_piattaforme(df_PLM_nomotore)[0]
        df_plm_no_piatt = bom.estrai_piattaforme(df_PLM_nomotore)[1]
        df_plm_piatt = df_plm_piatt.merge(transcod, how='left', left_on='Piattaforma', right_on='Piattaforma') # tabella transcod univoca, non moltiplica righe


        df_plm_piatt['MY25 vs MY24'] = np.where(df_plm_piatt['Piattaforma MY24'].astype(str)=='nan','Codice invariato','Codice nuovo')
        df_plm_piatt['MY25 vs MY24'] = np.where(df_plm_piatt['Piattaforma MY24'].astype(str)=='ND','Piattaforma non presente in MY24',df_plm_piatt['MY25 vs MY24']) 
        df_plm_piatt['Piattaforma MY24'] = df_plm_piatt['Piattaforma MY24'].fillna(df_plm_piatt['Piattaforma'])

        df_plm_piatt['key'] = df_plm_piatt['Piattaforma MY24']+df_plm_piatt['Articolo']
        count_dupl = df_plm_piatt[['key','Articolo']].groupby(by='key', as_index=False).count()
        count_dupl['Nota'] = np.where(count_dupl.Articolo >1, 'Chiave non univoca',None)
        count_dupl = count_dupl[['key','Nota']]

        df_plm_piatt = df_plm_piatt.merge(df_sap_piatt[layout['Merge_piattaforme']], how='left',left_on='key',right_on='key', suffixes=('_MY25','_MY24'))
        df_plm_piatt  = df_plm_piatt.merge(count_dupl, how='left',left_on='key',right_on='key')

        #pr.stampa(df_plm_piatt, 'PLM (MY25) | Piattaforme',layout, 'Piattaforme25')
        #st.write(df_plm_piatt)
        #pr.stampa(df_plm_no_piatt, 'PLM no piattaforme',layout,'STGR')
    if not st.toggle('Visulizza tutto'):    
        df_plm_piatt = df_plm_piatt[df_plm_piatt.STGR_MY24.astype(str) != 'Non popolato in MY24']
        

    pr.stampa(df_plm_piatt, 'PLM (MY25) | Piattaforme',layout,'Piattaforme25')
    st.divider()
    st.subheader(f'{len(df_plm_piatt)}')
    st.write('Righe da analizzare')
    st.divider()
    st.subheader('Download righe da analizzare piattaforme',divider='grey')
    pr.scarica_excel(df_plm_piatt[layout['Piattaforme25']['cols']], f'{sku} - Piattaforme.xlsx')

with OTHER:
    # sul df_sap_no_piatt metto in STGR 'non popolato...' 
    # merge su codice concatenato con M-V-X

    df_sap_no_piatt = bom.livello1(df_sap_no_piatt)
    df_sap_no_piatt['key'] = df_sap_no_piatt['L1']+df_sap_no_piatt['Articolo']+df_sap_no_piatt['Descr. Gruppo Tecnico']
    df_sap_no_piatt['STGR'] = df_sap_no_piatt['STGR'].fillna('Non popolato in MY24')

    df_plm_no_piatt = bom.livello1(df_plm_no_piatt)
    df_plm_no_piatt['key'] = df_plm_no_piatt['L1']+df_plm_no_piatt['Articolo']+df_plm_no_piatt['Descr. Gruppo Tecnico']
    count_dupl_flat = df_plm_no_piatt[['key','Articolo']].groupby(by='key', as_index=False).count()
    count_dupl_flat['Nota'] = np.where(count_dupl_flat.Articolo >1, 'Chiave non univoca',None)
    count_dupl_flat = count_dupl_flat[['key','Nota']]

    df_plm_no_piatt = df_plm_no_piatt.merge(df_sap_no_piatt[layout['Merge_no_piatt']], how='left',left_on='key', right_on='key',suffixes=('_MY25','_MY24'))
    df_plm_no_piatt = df_plm_no_piatt.merge(count_dupl_flat,how='left',left_on='key', right_on='key' )
    df_plm_no_piatt['Verifica'] = df_plm_no_piatt['STGR_MY24'] == df_plm_no_piatt['STGR_MY25']

    df_plm_no_piatt = df_plm_no_piatt[df_plm_no_piatt['STGR_MY24'] != 'Non popolato in MY24']
    df_plm_no_piatt = df_plm_no_piatt[df_plm_no_piatt.Verifica == False]
    df_plm_no_piatt = df_plm_no_piatt[df_plm_no_piatt.STGR_MY25.astype(str) == 'nan']
    
    df_plm_no_piatt = df_plm_no_piatt.reset_index(drop=True)
    pr.stampa(df_plm_no_piatt,'Livelli M-V-X senza piattaforma', layout, 'No_piatt')
   
    st.write('Righe totali: ',(len(df_plm_no_piatt)))
    st.write('Righe univoche: ',len(df_plm_no_piatt[df_plm_no_piatt.Nota.astype(str) != 'Chiave non univoca']))

    st.subheader('Download righe da analizzare M-V-X',divider='grey')
    pr.scarica_excel(df_plm_no_piatt[layout['No_piatt']['cols']], f'{sku} - M-V-X.xlsx')


