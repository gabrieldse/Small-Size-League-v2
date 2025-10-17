def sum_vectors(vector_a, vector_b):
    vector_a['x'] += vector_b['x']
    vector_a['y'] += vector_b['y']

    return vector_a

def norm_vector(vector_a):
    norm = (vector_a['x']**2 + vector_a['y']**2)**0.5
    vector_a['x'] /= norm
    vector_a['y'] /= norm

    return vector_a

def multi_vector(vector_a, scalar):
    vector_a['x'] *= scalar
    vector_a['y'] *= scalar

    return vector_a