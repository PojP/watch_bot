from dataclasses import dataclass
from typing import Union
import numpy as np

from rapidfuzz import fuzz
from rapidfuzz import utils

@dataclass(frozen=True)
class Episode:
    tg_id: Union[int,str]
    title: str
    search_amount: int
    year: Union[int, None]

def find_accuracy(episode: Episode, query: str):
    try:
        title_words_array=episode.title.split()
        query_words_array=query.split()

        length_accuracy_vector=0
        height_accuracy_array=0

        accuracy_array=[]
        destroy=True
        for i in query_words_array:
            accuracy_vector=[]
            for j in title_words_array:
                ratio=fuzz.QRatio(j,i,processor=utils.default_process)
                if ratio>=50:
                    accuracy_vector.append(ratio)
                    destroy=False
                else:
                    accuracy_vector.append(0)
            length_accuracy_vector=len(accuracy_vector)
            accuracy_array.append(accuracy_vector)
        if destroy:
            return [episode,0]
        height_accuracy_array=len(accuracy_array)
    
        last_diagonal_index=length_accuracy_vector-height_accuracy_array+1

        accuracy=np.array(accuracy_array)
    
        if last_diagonal_index<0:
            return [episode,0]
        if last_diagonal_index==0:
            last_diagonal_index+=1

        diagonales=[]
        for i in range(last_diagonal_index):
            if i==0:
                diagonales.append(int((np.diag(accuracy,i)).sum()*1.2/len(query_words_array)))
            else:
                diagonales.append( int( ((np.diag(accuracy,i) ).sum())/len(query_words_array)) )
        del accuracy
        full_title_case=(len(query)/len(episode.title))
        if full_title_case<=1.0 and full_title_case>0.7:
            return [episode,int(max(diagonales)*full_title_case)]
        return [episode,max(diagonales)]
    except Exception as e:
        return e
    #return [episode,int(max(diagonales)*(len(query)/len(episode.title)))]

def show_beatiful(episode,query_words,arr):
    print(f"          {episode.title}")
    for i in range(len(arr)):
        print(f"{query_words[i]}   {arr[i]}")

