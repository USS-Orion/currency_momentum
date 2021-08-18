#!/usr/bin/python3
# -*- encoding: utf-8 -*-
#currency momentum strategy(Menkhoff et al. 2012b)

import numpy as np
import pandas as pd
from pandas import *


def read_data(path='./exchange_rate.xlsx'):
    data = pd.read_excel(path,sheet_name=0,header=1,index_col=0)
    len_cols = len(data.columns)
    col=[1+3*i for i in range(int(len_cols/3))]
    data = data.iloc[:,col]

    return data

def make_dic(data):
    df = data.copy()
    columns = list(df.columns)
    keys = [columns[i] for i in range(0,int(len(columns)),2)]
    values = [columns[i] for i in range(1,int(len(columns)),2)]
    dic = dict()
    for kv in range(len(keys)):
        dic[keys[kv]] = values[kv]
    
    return dic
      
def evaluation_past(data,j=1,k=1):
    df = data.copy()
    df_now = df.iloc[:,[i for i in range(0,int(len(df.columns)),2)]]
    df_future = df.iloc[:,[i for i in range(1,int(len(df.columns)),2)]]
    pool = []
    winner_now = []
    loser_now = []
    index = []
    for i in range(len(df_now.index)):
        for p in range(len(df_now.columns)):
            tt = df_now.iat[i,p] * df_future.iat[i,p]
            if np.isnan(tt) == False:
                pool.append(p)
        df_temp = df_now.iloc[:,pool]
        income_rate = df_temp/df_temp.shift(j)
        income_rate_monthly = np.log(income_rate)/np.log(np.e)
        irm_i=income_rate_monthly.iloc[i,:]
        temp_list = irm_i.sort_values(ascending=False)
        # temp_list = temp_list.dropna(inplace=True)
        if len(temp_list) != 0:
            winner_now.append(list(temp_list[:5].index))
            loser_now.append(list(temp_list[-5:].index))
            index.append(i)

    return winner_now,loser_now,index

def estimate_future(data,j,k,w_list,l_list,ii):
    dic = make_dic(data)
    df = data.copy()
    winner_future = [dic[w_list[i]] for i in range(len(w_list))]
    loser_future = [dic[l_list[i]] for i in range(len(l_list))]
    df_columns = list(df.columns)
    for i in range(5):
        future_win_index = df_columns.index(winner_future[i])
        now_win_index = df_columns.index(w_list[i])
        future_lose_index = df_columns.index(loser_future[i])
        now_lose_index = df_columns.index(l_list[i])
        df['winner_{}'.format(i)] = (df.iloc[:,future_win_index] - df.iloc[:,now_win_index].shift(-1))/df.iloc[:,now_win_index]
        df['loser_{}'.format(i)] = (df.iloc[:,future_lose_index] - df.iloc[:,now_lose_index].shift(-1))/df.iloc[:,now_lose_index]
    winner_k = df.loc[:,['winner_{}'.format(n) for n in range(5)]]
    loser_k = df.loc[:,['loser_{}'.format(n) for n in range(5)]]
    winner_k['sum'] = winner_k.sum(axis=1)
    loser_k['sum'] = loser_k.sum(axis=1)
    m=0
    winner_k['sum_k'] = 0
    loser_k['sum_k'] = 0
    while m <= k:
        winner_k['sum_k'] = (winner_k['sum_k']+winner_k['sum'].shift(-m))/5
        loser_k['sum_k'] = (loser_k['sum_k']+loser_k['sum'].shift(-m))/5
        m += 1
    winner_loser = pd.concat([winner_k['sum_k'],loser_k['sum_k']],axis=1)
    winner_loser.columns = ['winner','loser']
    winner_loser['winner-loser'] = winner_loser['winner']- winner_loser['loser']
    winner_loser = winner_loser.iloc[ii,:]

    return winner_loser

def main():
    j=int(input("请输入formation_period_j:"))
    k=int(input("请输入holding_period_k:"))
    data = read_data()
    all_winners, all_losers, all_index = evaluation_past(data=data,j=j,k=k)
    all_winners_losers=pd.DataFrame({'winner':[],'loser':[],'winner-loser':[]}).T
    for ii in range(len(all_winners)):
        winner_loser = estimate_future(data=data,j=j,k=k,w_list=all_winners[ii],l_list=all_losers[ii],ii=all_index[ii])
        all_winners_losers[winner_loser.name] = winner_loser
    all_winners_losers=all_winners_losers.T
    all_winners_losers = all_winners_losers.iloc[j:-k,:]
    all_winners_losers.to_excel('./output_j={j}_k={k}.xls'.format(j=j,k=k))

    return all_winners_losers

if __name__=="__main__":
    outcome = main()

    print(outcome)
