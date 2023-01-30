import numpy as np
from lebedigital.unit_registry import ureg

@ureg.check('','')
def dummy_hydration_parameters(slag_ratio, phi_hydration) :
    """
    This is a dummy function to make the snakemake workflow work until the real function is ready
    It changes arbitrarily chosen values depending on slag content, not based on physics or anything.

    Parameters
    ----------
    slag_ratio : float / pint unitless
        amount of slag compared to cement, value from 0 to 1
    phi_hydration: ??
        input from Atuls parameter identification

    Returns
    -------
    B1 : float / pint unit will be in '1/s'
        hydration parameter
    B2 : float / pint unitless unit
        hydration parameter
    eta : float / pint unitless unit
        hydration parameter
    E_act : float / pint unit, will be in 'J/mol'
        activation energy - hydration parameter
    T_ref : float / pint unit, will be in 'degree Celsius'
        reference temperature - hydration parameter
    Q_pot : float / pint unit, will be in 'J/kg'
        maximum potential hydration parameter
    """

    # paste_youngs_modulus_min = 15 * ureg('GPa')
    # paste_youngs_modulus_max = 25 * ureg('GPa')
    # paste_youngs_modulus = paste_youngs_modulus_min + (paste_youngs_modulus_max-paste_youngs_modulus_min)*slag_ratio
    #
    # paste_strength_min = 8 * ureg('MPa')
    # paste_strength_max = 13 * ureg('MPa')
    # paste_strength = paste_strength_min + (paste_strength_max-paste_strength_min)*slag_ratio

    B1 = 2.916E-4 * ureg('1/s') # in 1/s
    B2 = 0.0024229 * ureg('') # -
    eta = 5.554 * ureg('') # something about diffusion
    E_act = 5653 * 8.3145 * ureg('J/mol') # activation energy in Jmol^-1
    Q_ = ureg.Quantity
    T_ref = Q_(25, ureg.degC)

    Q_pot_min = 100000 * ureg('J/kg')
    Q_pot_max = 300000 * ureg('J/kg')
    Q_pot = Q_pot_max - (Q_pot_max-Q_pot_min)*slag_ratio

    return B1, B2, eta, E_act, Q_pot, T_ref

if __name__ == "__main__":
    # test while developing this

    print(dummy_hydration_parameters(1,10))
