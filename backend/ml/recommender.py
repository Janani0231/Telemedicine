import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def recommend_items(user_input):
    # Create a simple recommendation DataFrame
    recommendations = pd.DataFrame({
        'item_id': range(1, 6),
        'name': ['Item ' + str(i) for i in range(1, 6)],
        'score': np.random.random(5)
    })
    
    # Sort by score
    recommendations = recommendations.sort_values('score', ascending=False)
    
    return recommendations
