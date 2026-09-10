from capytale.autoeval import ValidateFunction
from math import sqrt, pi, prod, isclose


class ValidateFunctionApprox(ValidateFunction):
    """
    Variante de ValidateFunction avec une comparaison plus souple
    pour les résultats flottants.
    """
    def equality(self, a, b):
        if isinstance(a, float) or isinstance(b, float):
            try:
                return isclose(a, b, rel_tol=1e-6, abs_tol=1e-9)
            except TypeError:
                return False
        return a == b

valeurs = [-10, -3, -1, 0, 1, 4, 9, 25, 2.25]

test_carre = ValidateFunction(
    "carre",
    test_values = valeurs,
    target_values = [x**2 for x in valeurs]
)
    
test_racine_carree = ValidateFunctionApprox(
    "racine_carree",
    test_values = valeurs,
    target_values = [ "x ne prend pas une valeur convenable !" if x < 0 else x**0.5 for x in valeurs ]
)

def signe_sol(x):
    if x > 0:
        return "positif"
    elif x < 0:
        return "négatif"
    else:
        return "nul"

test_signe = ValidateFunction(
    "signe",
    test_values = valeurs,
    target_values = [ signe_sol(x) for x in valeurs ]
)

couples_valeurs = [(5, 2), (-3, 4), (0, 1), (0, -2), (0.0001, 0), (7,7), (-5, -5), (3.5, 2.5), (-1.5, -2.5), (0, 0)]

test_maximum = ValidateFunction(
    "maximum",
    test_values = couples_valeurs,
    target_values = [max(pair) for pair in couples_valeurs]
)

test_minimum = ValidateFunction(
    "minimum",
    test_values = couples_valeurs,
    target_values = [min(pair) for pair in couples_valeurs]
)


points = [
    (0, 0, 3, 4),
    (1, 1, 1, 1),
    (-1, 0, 1, 0),
    (0, -2, 0, 5),
    (-2, -3, 1, 1),
    (1.5, 2.5, 4.5, 6.5)
]


def distance_sol(xA, yA, xB, yB):
    return sqrt((xB - xA)**2 + (yB - yA)**2)


test_distance = ValidateFunctionApprox(
    "distance",
    test_values=points,
    target_values=[distance_sol(xA, yA, xB, yB) for xA, yA, xB, yB in points]
)


trapezes = [
    (3, 5, 2),
    (4, 10, 3),
    (2, 2, 5),
    (0, 6, 4),
    (2.5, 7.5, 3)
]


def aire_trapeze_sol(b, B, h):
    return (b + B) * h / 2


test_aire_trapeze = ValidateFunctionApprox(
    "aire_trapeze",
    test_values=trapezes,
    target_values=[aire_trapeze_sol(b, B, h) for b, B, h in trapezes]
)


rayons = [0, 1, 2, 5, 10, 2.5]


test_circonference_cercle = ValidateFunctionApprox(
    "circonference_cercle",
    test_values=rayons,
    target_values=[2 * pi * r for r in rayons]
)


listes_produit = [
    (5,),
    (2, 3, 4),
    (10, -2),
    (2, 0, 8),
    (0.5, 4, 2),
    (-1, -2, -3)
]


test_produit = ValidateFunctionApprox(
    "produit",
    test_values=listes_produit,
    target_values=[prod(t) for t in listes_produit]
)


listes_moyenne = [
    (10, 12, 14),
    (20, 10),
    (7,),
    (0, 10, 20),
    (2.5, 3.5, 4.5),
    (-2, 2)
]


def moyenne_sol(*nombres):
    return sum(nombres) / len(nombres)


test_moyenne = ValidateFunctionApprox(
    "moyenne",
    test_values=listes_moyenne,
    target_values=[moyenne_sol(*t) for t in listes_moyenne]
)


listes_pairs = [
    (1, 2, 3, 4, 5, 6),
    (1, 3, 5),
    (2, 4, 6, 8),
    (-2, -3, 0, 7),
    (-4, -2, 0, 1, 3, 5)
]


def compte_pairs_sol(*nombres):
    return sum(1 for n in nombres if n % 2 == 0)


test_compte_pairs = ValidateFunction(
    "compte_pairs",
    test_values=listes_pairs,
    target_values=[compte_pairs_sol(*t) for t in listes_pairs]
)


valeurs_cube = [-5, -3, -1, 0, 1, 2, 4, 10, 0.5]


test_cube = ValidateFunctionApprox(
    "cube",
    test_values=valeurs_cube,
    target_values=[x**3 for x in valeurs_cube]
)