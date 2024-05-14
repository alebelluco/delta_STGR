# Package per le operazioni sulle BOM
# AB_10/05/2024
#
# -------------------------------------------------

import pandas as pd 

def rimuovi_motore(df):
    df['elimina'] = False
    for i in range(len(df)):
        codice = str(df.Articolo.iloc[i])
        if codice[0:4]=='0029':
            df.elimina.iloc[i]=True
            livello = df['Liv.'].iloc[i]
            riga = i
            for j in range(riga+1, len(df)):
                liv_check = df['Liv.'].iloc[j]
                if liv_check > livello:
                    df.elimina.iloc[j]=True
                else:
                    break    
    df = df[df.elimina == False]
    df = df.reset_index(drop=True)
    df = df.drop(columns=['elimina'])
    return df

def estrai_piattaforme(df):
    '''
    Funzione con doppio return
    --------------------------
    [0] = piattaforme \n
    [1] = no_piattaforme
    '''
    codici_piattaforma = ['P','S','T']
    df['piattaforma']=False
    df['Piattaforma']=None
    df['Desc_piattaforma']=None
    for i in range(len(df)):
        art = str(df.Articolo.iloc[i])[3:4]
        if any([digit in art for digit in codici_piattaforma]):
            df['piattaforma'].iloc[i]=True
            piattaforma = df.Articolo.iloc[i]
            desc_piatt = df['Testo breve oggetto'].iloc[i]
            df['Piattaforma'].iloc[i]=piattaforma
            df['Desc_piattaforma'].iloc[i]=desc_piatt

            liv = df['Liv.'].iloc[i]
            if i != len(df):
                for j in range(i+1, (len(df))):
                    liv_check = df['Liv.'].iloc[j]
                    if liv_check > liv:
                        df.piattaforma.iloc[j] = True
                        df['Piattaforma'].iloc[j]=piattaforma
                        df['Desc_piattaforma'].iloc[j]=desc_piatt
                    else:
                        break
    piattaforme = df[df.piattaforma == True].reset_index(drop=True)
    no_piatt = df[df.piattaforma == False].reset_index(drop=True)

    return piattaforme, no_piatt
    
def livello1(df):
    '''
    NOTA
    ---
    Da applicare dopo aver tolto il motore
    '''
    livelli1 = ['M','V','X']
    df['L1']=None
    for i in range(len(df)):
        art = str(df.Articolo.iloc[i])[0:1]
        if any([digit in art for digit in livelli1]):
            df.L1.iloc[i] = art
            if i != len(df):
                for j in range(i+1, len(df)):
                    check = str(df.Articolo.iloc[j])[0:1]
                    if all([digit not in check for digit in livelli1]):
                        df.L1.iloc[j] = art
                    else:
                        break

    return df

        


        
