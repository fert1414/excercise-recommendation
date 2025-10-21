import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

def feature_constructor(dif_level, gender, exp_level, target_muscle):
    features_string = dif_level + ' ' + \
        gender + ' ' + \
        exp_level + ' ' + \
        target_muscle
    
    return features_string

class RecommendationSystem:
    def __init__(self, data):
        self.data = pd.DataFrame(columns = ['combined_data', 'excercises'])
        self.data['combined_data'] = feature_constructor(
            data['Difficulty Level'].astype(str), 
            data['Gender'].astype(str),
            data['Experience_Level'].astype(str),
            data['Target Muscle Group_Cleaned'].astype(str))
        self.data['excercises'] = data['Exercise_Base']
        
        self.vectorizer_for_predict = TfidfVectorizer()
        self.feature_matrix = self.vectorizer_for_predict.fit_transform(self.data['combined_data'])

    def get_recommendation(self, gender, exp_level, target_muscle, dif_level, top_number = 5):
        input_data = self.vectorizer_for_predict.transform([feature_constructor(dif_level, gender, str(exp_level), target_muscle)])
        self.similitary_distance = cosine_similarity(input_data, self.feature_matrix)[0]
        self.similitary_distance = [(i, x) for i, x in enumerate(self.similitary_distance)]

        self.similitary_distance.sort(key = lambda x: x[1], reverse = True)

        results = []
        for i in self.similitary_distance:
            result = self.data.iloc[i[0]]['excercises']
            if result not in results:
                results.append(result)

            if len(results) == top_number:
                break

        print(Counter(results).items())

        return results