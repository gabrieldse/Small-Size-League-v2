import math
def sum_vectors(vector_a, vector_b):
    """Soma dois vetores (dicts) e retorna um NOVO dict."""
    return {
        'x': vector_a['x'] + vector_b['x'],
        'y': vector_a['y'] + vector_b['y']
    }

def norm_vector(vector):
    """Normaliza um vetor (dict) e retorna um NOVO dict com a direção."""
    norm = (vector['x']**2 + vector['y']**2)**0.5
    
    if norm == 0:
        return {'x': 0, 'y': 0} 
    
    return {
        'x': vector['x'] / norm,
        'y': vector['y'] / norm
    }

def multi_vector(vector, scalar):
    """Multiplica um vetor (dict) por um escalar e retorna um NOVO dict."""
    return {
        'x': vector['x'] * scalar,
        'y': vector['y'] * scalar
    }

def angle_diff(target, current):
    """
    Calcula a menor diferença entre dois ângulos (em radianos).
    Garante que o resultado esteja entre -pi e +pi.
    """
    diff = target - current
    
    while diff > math.pi: 
        diff -= 2 * math.pi
    while diff < -math.pi: 
        diff += 2 * math.pi
        
    return diff