from time import perf_counter

def chrono(f, *args, nb=1000, **kwargs):
    debut = perf_counter()
    for _ in range(nb):
        resultat = f(*args, **kwargs)
    duree = (perf_counter() - debut) / nb
    return resultat, duree